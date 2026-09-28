import pickle, json, sys, numpy as np, pandas as pd
import model_core as M
from model_core import build_samples, _fit_predict_crps
M.QLEVELS=np.round(np.arange(0.1,0.91,0.133),3)   # ~7 quantile levels
M.LGB["num_leaves"]=16
dom=sys.argv[1]; maxn=int(sys.argv[2])
if dom=="hkust":
    import load_hkust as L; c=pickle.load(open("data/hkust_cache_full.pkl","rb")); frames=c["frames"]; EXO=L.EXO; stride=None
else:
    import load_camels as L; c=pickle.load(open("data/camels/camels_cache.pkl","rb")); frames=c["frames"]; EXO=L.EXO; stride=10
frames=frames[:maxn]; out=[]
for fr in frames:
    if dom=="hkust":
        fr=fr.copy(); cap=np.nanpercentile(fr["y"],99)
        if cap>0: fr["y"]=fr["y"]/cap
    keep=pd.Index(sorted(fr.index[::stride])) if stride else None
    long,feats=build_samples(fr,"D",7,EXO,keep_origins=keep)
    origins=np.sort(long["origin"].unique()); cut=origins[int(len(origins)*0.8)]
    tr=(long["origin"]<=(cut-pd.Timedelta(7,"D"))).values; te=(long["origin"]>cut).values
    if te.sum()<40: continue
    m={cfg:float(_fit_predict_crps(long,feats[cfg],tr,te,n_est=40).mean()) for cfg in ["clim","climfut","persist","hist","full"]}
    Ccl,Ccf,Cp,Ch,Cf=m["clim"],m["climfut"],m["persist"],m["hist"],m["full"]
    if Ccl<=1e-9: continue
    exo0=(Ccl-Ccf)/Ccl; exo=(Ch-Cf)/Ccl
    out.append({"endo":(Ccl-Ch)/Ccl,"exo":exo,"pshr":(Ccl-Cp)/Ccl,
                "redu_frac":(exo0-exo)/exo0 if exo0>1e-3 else None})
json.dump(out,open(f"out/perseries_{dom}.json","w")); print(dom,"usable series =",len(out))
