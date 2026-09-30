"""Value of an imperfect forecast: the future forcing in the 'full' model is replaced by
x_{t+k} + e, e ~ N(0, (lam*sd_c)^2) independently per variable, where sd_c is that
variable's standard deviation. The model is trained and tested on the degraded forcing.
rho_exo(lam) = (CRPS_hist - CRPS_full(lam)) / CRPS_clim  (primary configuration)."""
import pickle, json, sys, numpy as np, pandas as pd
from model_core import build_samples, _fit_predict_crps
LAMS=[0.0,0.25,0.5,1.0]
def run(name, frames, exo, stride=None, seed=0):
    longs=[]; feats=None
    for fr in frames:
        keep=pd.Index(sorted(fr.index[::stride])) if stride else None
        lg,feats=build_samples(fr,"D",7,exo,keep_origins=keep); longs.append(lg)
    long=pd.concat(longs,ignore_index=True)
    o=np.sort(long["origin"].unique()); cut=o[int(len(o)*0.8)]
    tr=(long["origin"]<=cut-pd.Timedelta(7,"D")).values; te=(long["origin"]>cut).values
    Ccl=float(_fit_predict_crps(long,feats["clim"],tr,te,n_est=150).mean())
    Ch =float(_fit_predict_crps(long,feats["hist"],tr,te,n_est=150).mean())
    fut=[c for c in feats["full"] if c.startswith("fut_")]; rng=np.random.default_rng(seed); out=[]
    for lam in LAMS:
        L=long.copy()
        for c in fut:
            sd=float(np.nanstd(L[c].values)); L[c]=L[c].values+rng.normal(0,lam*sd,len(L))
        Cf=float(_fit_predict_crps(L,feats["full"],tr,te,n_est=150).mean())
        out.append(dict(lam=lam,rho_exo=(Ch-Cf)/Ccl)); print(f"  {name} lam={lam:.2f} rho_exo={(Ch-Cf)/Ccl:.3f}",flush=True)
    for r in out: r["retained"]=r["rho_exo"]/out[0]["rho_exo"] if out[0]["rho_exo"]>1e-6 else None
    return dict(domain=name,CRPS_clim=Ccl,CRPS_hist=Ch,curve=out)
dom=sys.argv[1]
if dom=="kelmarsh":
    import load_kelmarsh as L; r=run("Kelmarsh(wind)",pickle.load(open("data/kelmarsh_cache.pkl","rb"))["frames"],L.EXO)
elif dom in ("DKASC_site13","DKASC_M9","DKASC_site31"):
    import load_dkasc as L, dkasc_rc; r=run(dom,[dkasc_rc.load(dom,"D")],L.EXO)
elif dom=="camels":
    import load_camels as L; r=run("CAMELS(streamflow)",pickle.load(open("data/camels/camels_cache.pkl","rb"))["frames"][::2],L.EXO,stride=21)
elif dom=="hkust":
    import load_hkust as L
    fr=[]
    for f in pickle.load(open("data/hkust_cache_full.pkl","rb"))["frames"]:
        f=f.copy(); q=np.nanpercentile(f["y"],99); f["y"]=f["y"]/q if q>0 else f["y"]; fr.append(f)
    r=run("HKUST(subtropical PV)",fr,L.EXO,stride=2)
json.dump(r,open(f"out/degrade_{dom}.json","w"),indent=2)
