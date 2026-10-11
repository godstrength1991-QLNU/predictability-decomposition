"""Refit variability: the primary configuration is refitted with different random seeds
(row and column subsampling are random); data, split and settings are unchanged."""
import pickle, json, sys, os, time, numpy as np, pandas as pd
import model_core as M
from model_core import build_samples, _fit_predict_crps
def prep(frames, exo, stride=None):
    longs=[]; feats=None
    for fr in frames:
        keep=pd.Index(sorted(fr.index[::stride])) if stride else None
        lg,feats=build_samples(fr,"D",7,exo,keep_origins=keep); longs.append(lg)
    long=pd.concat(longs,ignore_index=True); o=np.sort(long["origin"].unique()); cut=o[int(len(o)*0.8)]
    tr=(long["origin"]<=cut-pd.Timedelta(7,"D")).values; te=(long["origin"]>cut).values
    return long,feats,tr,te
def load(dom):
    if dom=="kelmarsh":
        import load_kelmarsh as L; return pickle.load(open("data/kelmarsh_cache.pkl","rb"))["frames"],L.EXO,None
    if dom.startswith("DKASC"):
        import load_dkasc as L, dkasc_rc; return [dkasc_rc.load(dom,"D")],L.EXO,None
    if dom=="camels":
        import load_camels as L; return pickle.load(open("data/camels/camels_cache.pkl","rb"))["frames"][::2],L.EXO,21
    if dom=="reservoir":
        import load_reservoir as L; return pickle.load(open("data/reservoir_full_cache.pkl","rb"))["frames"],L.EXO,200
    if dom=="hkust":
        import load_hkust as L
        fr=[]
        for f in pickle.load(open("data/hkust_cache_full.pkl","rb"))["frames"]:
            f=f.copy(); q=np.nanpercentile(f["y"],99); f["y"]=f["y"]/q if q>0 else f["y"]; fr.append(f)
        return fr,L.EXO,2
if __name__=="__main__":
    dom=sys.argv[1]; seeds=[int(s) for s in sys.argv[2].split(",")]
    frames,exo,stride=load(dom); long,feats,tr,te=prep(frames,exo,stride)
    fn=f"out/refit_{dom}.json"; res=json.load(open(fn)) if os.path.exists(fn) else {"domain":dom,"runs":[]}
    done={r["seed"] for r in res["runs"]}
    for s in seeds:
        if s in done: continue
        t=time.time(); M.LGB["random_state"]=s
        C={c:float(_fit_predict_crps(long,feats[c],tr,te,n_est=150).mean()) for c in ["clim","hist","full"]}
        r=dict(seed=s,rho_endo=(C["clim"]-C["hist"])/C["clim"],rho_exo=(C["hist"]-C["full"])/C["clim"])
        res["runs"].append(r); json.dump(res,open(fn,"w"),indent=2)
        print(f"  {dom} seed {s}: endo={r['rho_endo']:.4f} exo={r['rho_exo']:.4f}  ({time.time()-t:.0f}s)",flush=True)
    M.LGB["random_state"]=0
