"""Rolling-origin evaluation: three consecutive test blocks (55-70%, 70-85%, 85-100% of
forecast origins); each block is predicted by a model trained only on origins before it,
with an H-step embargo. Primary configuration (13 quantiles, 150 trees)."""
import pickle, json, sys, numpy as np, pandas as pd
from model_core import build_samples, _fit_predict_crps
BLOCKS=[(0.55,0.70),(0.70,0.85),(0.85,1.00)]
import os
ONLY=os.environ.get("ONLY")
if ONLY: BLOCKS=[BLOCKS[int(ONLY)]]
def rolling(name, frames, exo, stride=None):
    longs=[]; feats=None
    for fr in frames:
        keep=pd.Index(sorted(fr.index[::stride])) if stride else None
        lg,feats=build_samples(fr,"D",7,exo,keep_origins=keep); longs.append(lg)
    long=pd.concat(longs,ignore_index=True); o=np.sort(long["origin"].unique()); out=[]
    for a,b in BLOCKS:
        lo,hi=o[int(len(o)*a)], o[min(int(len(o)*b),len(o)-1)]
        tr=(long["origin"]<=lo-pd.Timedelta(7,"D")).values
        te=((long["origin"]>lo)&(long["origin"]<=hi)).values
        C={c:float(_fit_predict_crps(long,feats[c],tr,te,n_est=150).mean()) for c in ["clim","hist","full"]}
        r=dict(block=f"{int(a*100)}-{int(b*100)}%",rho_endo=(C["clim"]-C["hist"])/C["clim"],rho_exo=(C["hist"]-C["full"])/C["clim"],n_test=int(te.sum()))
        out.append(r); print(f"  {name} block {r['block']}: endo={r['rho_endo']:.3f} exo={r['rho_exo']:.3f} (n={r['n_test']})",flush=True)
    return dict(domain=name,blocks=out)
dom=sys.argv[1]
if dom=="kelmarsh":
    import load_kelmarsh as L; r=rolling("Kelmarsh(wind)",pickle.load(open("data/kelmarsh_cache.pkl","rb"))["frames"],L.EXO)
elif dom=="site13":
    import load_dkasc as L, dkasc_rc; r=rolling("DKASC_site13",[dkasc_rc.load("DKASC_site13","D")],L.EXO)
elif dom=="M9":
    import load_dkasc as L, dkasc_rc; r=rolling("DKASC_M9",[dkasc_rc.load("DKASC_M9","D")],L.EXO)
elif dom=="site31":
    import load_dkasc as L, dkasc_rc; r=rolling("DKASC_site31",[dkasc_rc.load("DKASC_site31","D")],L.EXO)
elif dom=="reservoir":
    import load_reservoir as L; r=rolling("Reservoir(ASOS-net)",pickle.load(open("data/reservoir_full_cache.pkl","rb"))["frames"],L.EXO,stride=300)
fn=f"out/rolling_{dom}.json"
if ONLY and os.path.exists(fn):
    old=json.load(open(fn)); old["blocks"]=[b for b in old["blocks"] if b["block"]!=r["blocks"][0]["block"]]+r["blocks"]; r=old
json.dump(r,open(fn,"w"),indent=2)
