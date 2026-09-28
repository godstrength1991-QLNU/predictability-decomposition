import pickle, json, numpy as np
from model_core import run_pooled_enriched
from load_hkust import EXO
c=pickle.load(open("data/hkust_cache_full.pkl","rb"))
frames=[]
for fr in c["frames"]:
    fr=fr.copy(); cap=np.nanpercentile(fr["y"],99)      # per-site capacity proxy
    if cap>0: fr["y"]=fr["y"]/cap
    frames.append(fr)
r=run_pooled_enriched("HKUST(capacity-normalised)", frames, "D",7, EXO, subsample_origin=2, n_est=150)
json.dump(r, open("out/enr_hkust_norm.json","w"), indent=2)
old=json.load(open("out/enr_hkust.json"))
print("\n              exo|clim  exo|hist  redundancy_frac")
print(f"raw (pooled)   {old['exo_given_clim']:.3f}    {old['rho_exo_c']:.3f}    {old['redundancy_frac']*100:.0f}%")
print(f"cap-normalised {r['exo_given_clim']:.3f}    {r['rho_exo_c']:.3f}    {r['redundancy_frac']*100:.0f}%")
