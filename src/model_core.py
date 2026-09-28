"""Predictability-decomposition engine (domain-agnostic).

Three models share the same learner and hyperparameters; only the inputs change:
  persist : calendar + current value y_t            (zero dynamic-information reference)
  hist    : persist + target lags + past exogenous  (all information available at forecast time)
  full    : hist    + future exogenous at t+k       (oracle / perfect forecast)

Metric (CRPS via averaged pinball over a quantile grid; same grid for all three):
  rho_endo = (CRPS_persist - CRPS_hist) / CRPS_persist   # value of history (endogenous)
  rho_exo  = (CRPS_hist   - CRPS_full ) / CRPS_persist   # value of future forcing (exogenous)
"""
import numpy as np, pandas as pd, lightgbm as lgb

QLEVELS = np.round(np.arange(0.05,0.96,0.075),3)         # 13 quantile levels
LGB = dict(n_estimators=300, learning_rate=0.05, num_leaves=31,
           min_child_samples=50, subsample=0.8, colsample_bytree=0.8,
           subsample_freq=1, random_state=0, n_jobs=-1, verbose=-1)

LAGS = {"D":[1,2,3,5,7,14,21,30], "h":[1,2,3,6,12,24]}
ROLL = {"D":[7,14,30],       "h":[6,24]}

def _calendar(idx, freq):
    doy = idx.dayofyear.values.astype("float32")
    out = {"doy_sin":np.sin(2*np.pi*doy/365.25), "doy_cos":np.cos(2*np.pi*doy/365.25)}
    if freq=="h":
        hr = idx.hour.values.astype("float32")
        out["hr_sin"]=np.sin(2*np.pi*hr/24); out["hr_cos"]=np.cos(2*np.pi*hr/24)
    return pd.DataFrame(out, index=idx)

def build_samples(frame, freq, H, exo_cols, keep_origins=None):
    """Return long df: one row per (origin, lead) with persist/hist/full feature blocks + target."""
    frame = frame.sort_index()
    y = frame["y"].astype("float32")
    cal = _calendar(frame.index, freq)
    # origin-time (info available at forecast time)
    base = pd.DataFrame(index=frame.index)
    base["y_now"] = y                                   # persist block
    for L in LAGS[freq]: base[f"ylag{L}"] = y.shift(L)   # hist: target lags
    for r in ROLL[freq]: base[f"yroll{r}"] = y.shift(1).rolling(r).mean()
    for c in exo_cols:                                   # hist: past exogenous (current + recent mean)
        base[f"{c}_now"]  = frame[c]
        base[f"{c}_roll"] = frame[c].shift(1).rolling(ROLL[freq][-1]).mean()
    persist_cols = ["y_now"]
    hist_cols    = persist_cols + [f"ylag{L}" for L in LAGS[freq]] + [f"yroll{r}" for r in ROLL[freq]] \
                   + [f"{c}_now" for c in exo_cols] + [f"{c}_roll" for c in exo_cols]

    rows=[]
    for k in range(1,H+1):
        d = base.copy()
        d["lead"] = np.float32(k)
        # calendar of the target time (t+k)
        tcal = cal.shift(-k); d = d.join(tcal.add_prefix("tgt_"))
        # future exogenous at target (oracle) -> full block
        for c in exo_cols: d[f"fut_{c}"] = frame[c].shift(-k).astype("float32")
        d["target"] = y.shift(-k)
        d["origin"] = frame.index
        d = d.dropna(subset=["target"])
        if keep_origins is not None: d = d[d["origin"].isin(keep_origins)]
        rows.append(d)
    long = pd.concat(rows, ignore_index=True)
    cal_cols = ["lead"]+[f"tgt_{c}" for c in cal.columns]
    fut_cols = [f"fut_{c}" for c in exo_cols]
    feats = {"clim":    cal_cols,
             "climfut": cal_cols+fut_cols,
             "persist": cal_cols+persist_cols,
             "hist":    cal_cols+hist_cols,
             "full":    cal_cols+hist_cols+fut_cols}
    return long, feats

def _crps_from_quantiles(Q, y):
    """Q: (n,levels) predicted quantiles (row-sorted). CRPS = 2*mean_level pinball."""
    Q = np.sort(Q, axis=1)                               # enforce monotone quantiles
    y = y[:,None]
    tau = QLEVELS[None,:]
    e = y - Q
    pin = np.where(e>=0, tau*e, (tau-1)*e)               # pinball per level
    return 2*pin.mean(axis=1)                            # per-sample CRPS

def _fit_predict_crps(long, cols, tr, te, n_est=300):
    Xtr, ytr = long.loc[tr, cols].values.astype("float32"), long.loc[tr,"target"].values.astype("float32")
    Xte, yte = long.loc[te, cols].values.astype("float32"), long.loc[te,"target"].values.astype("float32")
    Q = np.empty((len(yte), len(QLEVELS)), "float32")
    for j,q in enumerate(QLEVELS):
        p=dict(LGB); p["n_estimators"]=n_est
        m = lgb.LGBMRegressor(objective="quantile", alpha=float(q), **p)
        m.fit(Xtr, ytr)
        Q[:,j] = m.predict(Xte)
    return _crps_from_quantiles(Q, yte)                  # per-sample CRPS on test

def _rho_from_long(name, long, feats, freq, H, daytime_only, test_frac, n_est):
    origins = np.sort(long["origin"].unique())
    cut = origins[int(len(origins)*(1-test_frac))]
    emb = pd.Timedelta(H, "D" if freq=="D" else "h")
    tr = (long["origin"] <= (cut - emb)).values
    te = (long["origin"] >  cut).values
    if daytime_only:
        te = te & (long["target"].values > 0.02*np.nanmax(long["target"].values))
    out={}
    for cfg in ["clim","persist","hist","full"]:
        out[cfg] = float(np.mean(_fit_predict_crps(long, feats[cfg], tr, te, n_est=n_est)))
    Ccl,Cp,Ch,Cf = out["clim"],out["persist"],out["hist"],out["full"]
    # persistence-normalised: value of history/forcing beyond the current value
    rep,rxp = (Cp-Ch)/Cp, (Ch-Cf)/Cp
    # climatology-normalised: inertia counts as endogenous
    rec,rxc = (Ccl-Ch)/Ccl, (Ch-Cf)/Ccl
    persist_share=(Ccl-Cp)/Ccl
    res = dict(domain=name, freq=freq, H=H, n_test=int(te.sum()),
               CRPS_clim=Ccl, CRPS_persist=Cp, CRPS_hist=Ch, CRPS_full=Cf,
               rho_endo_p=rep, rho_exo_p=rxp, rho_endo_c=rec, rho_exo_c=rxc,
               persist_share=persist_share)
    print(f"[{name} | {freq} H={H}] Ccl={Ccl:.4f} Cp={Cp:.4f} Ch={Ch:.4f} Cf={Cf:.4f}\n"
          f"    persist-norm: endo={rep:.3f} exo={rxp:.3f} | clim-norm: endo={rec:.3f} exo={rxc:.3f} "
          f"| persist_share={persist_share:.3f}  (n_test={res['n_test']:,})")
    return res

def run_pooled(name, frames, freq, H, exo_cols, test_frac=0.2, n_est=300, subsample_origin=None):
    """Multiple target series sharing exogenous forcing (reservoirs / PV stations)."""
    longs=[]; feats=None
    for fr in frames:
        keep = pd.Index(sorted(fr.index[::subsample_origin])) if subsample_origin else None
        lg,feats = build_samples(fr, freq, H, exo_cols, keep_origins=keep)
        longs.append(lg)
    long = pd.concat(longs, ignore_index=True)
    return _rho_from_long(name, long, feats, freq, H, False, test_frac, n_est)

def run_domain(name, frame, freq, H, exo_cols, daytime_only=False, test_frac=0.2, subsample_origin=None, n_est=300):
    keep = pd.Index(sorted(frame.index[::subsample_origin])) if subsample_origin else None
    long, feats = build_samples(frame, freq, H, exo_cols, keep_origins=keep)
    return _rho_from_long(name, long, feats, freq, H, daytime_only, test_frac, n_est)


# ===== Enriched: synergy/redundancy + block-bootstrap CIs =====
def _boot_ci(sums, ns, nboot, seed=0):
    rng=np.random.default_rng(seed); U=len(ns); out={k:[] for k in ["endo","exo","pshr","redu"]}
    for _ in range(nboot):
        idx=rng.integers(0,U,U); n=ns[idx].sum()
        m={c:sums[c][idx].sum()/n for c in sums}
        Ccl,Ccf,Cp,Ch,Cf=m["clim"],m["climfut"],m["persist"],m["hist"],m["full"]
        endo=(Ccl-Ch)/Ccl; exo=(Ch-Cf)/Ccl; pshr=(Ccl-Cp)/Ccl; exo0=(Ccl-Ccf)/Ccl
        out["endo"].append(endo); out["exo"].append(exo); out["pshr"].append(pshr); out["redu"].append(exo0-exo)
    return {k:[round(float(np.percentile(v,2.5)),3),round(float(np.percentile(v,97.5)),3)] for k,v in out.items()}

def _enriched_from_long(name, long, feats, freq, H, daytime_only, test_frac, n_est, nboot=300):
    origins=np.sort(long["origin"].unique()); cut=origins[int(len(origins)*(1-test_frac))]
    emb=pd.Timedelta(H,"D" if freq=="D" else "h")
    tr=(long["origin"]<=(cut-emb)).values; te=(long["origin"]>cut).values
    if daytime_only: te=te&(long["target"].values>0.02*np.nanmax(long["target"].values))
    cfgs=["clim","climfut","persist","hist","full"]
    crps={c:_fit_predict_crps(long,feats[c],tr,te,n_est=n_est) for c in cfgs}
    Ccl,Ccf,Cp,Ch,Cf=[float(crps[c].mean()) for c in cfgs]
    endo=(Ccl-Ch)/Ccl; exo=(Ch-Cf)/Ccl; pshr=(Ccl-Cp)/Ccl
    exo0=(Ccl-Ccf)/Ccl; redu=exo0-exo; rfrac=redu/exo0 if exo0>1e-9 else float("nan")
    oid=long["origin"].values[te]; _,inv=np.unique(oid,return_inverse=True); ns=np.bincount(inv)
    sums={c:np.bincount(inv,weights=crps[c]) for c in cfgs}
    ci=_boot_ci(sums,ns,nboot)
    res=dict(domain=name,freq=freq,H=H,n_test=int(te.sum()),
        CRPS_clim=Ccl,CRPS_climfut=Ccf,CRPS_persist=Cp,CRPS_hist=Ch,CRPS_full=Cf,
        rho_endo_c=endo,rho_exo_c=exo,persist_share=pshr,
        exo_given_clim=exo0,redundancy=redu,redundancy_frac=rfrac,
        ci_endo=ci["endo"],ci_exo=ci["exo"],ci_pshr=ci["pshr"],ci_redu=ci["redu"])
    print(f"[{name} | {freq} H={H}] endo={endo:.3f} CI{ci['endo']}  exo={exo:.3f} CI{ci['exo']}  "
          f"pshr={pshr:.3f}  exo|clim={exo0:.3f}  REDUND={redu:.3f} ({rfrac:.0%}) CI{ci['redu']}  n={int(te.sum())}")
    return res

def run_pooled_enriched(name,frames,freq,H,exo_cols,test_frac=0.2,n_est=150,subsample_origin=None,nboot=300):
    longs=[]; feats=None
    for fr in frames:
        keep=pd.Index(sorted(fr.index[::subsample_origin])) if subsample_origin else None
        lg,feats=build_samples(fr,freq,H,exo_cols,keep_origins=keep); longs.append(lg)
    return _enriched_from_long(name,pd.concat(longs,ignore_index=True),feats,freq,H,False,test_frac,n_est,nboot)

def run_domain_enriched(name,frame,freq,H,exo_cols,daytime_only=False,test_frac=0.2,n_est=150,subsample_origin=None,nboot=300):
    keep=pd.Index(sorted(frame.index[::subsample_origin])) if subsample_origin else None
    long,feats=build_samples(frame,freq,H,exo_cols,keep_origins=keep)
    return _enriched_from_long(name,long,feats,freq,H,daytime_only,test_frac,n_est,nboot)
