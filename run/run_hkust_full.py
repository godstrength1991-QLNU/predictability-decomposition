import pickle, json, time
from model_core import run_pooled
from load_hkust import EXO
c=pickle.load(open("data/hkust_cache_full.pkl","rb"))
t=time.time()
r=run_pooled("HKUST(subtropical PV)", c["frames"], "D", 7, EXO, subsample_origin=2, n_est=200)
r["n_sites"]=len(c["frames"]); r["note"]="full 58/60 sites"
print(f"    {time.time()-t:.0f}s ({len(c['frames'])} sites)")
json.dump(r, open("out/rho_hkust_full.json","w"), indent=2)
# compare to 18-site version
old={x["domain"]:x for x in json.load(open("out/rho_B.json"))}["HKUST(subtropical PV)"]
print("\n            persist_share  rho_endo_c  rho_exo_c")
print(f"18 sites     {old['persist_share']:.3f}       {old['rho_endo_c']:.3f}     {old['rho_exo_c']:.3f}")
print(f"58 sites     {r['persist_share']:.3f}       {r['rho_endo_c']:.3f}     {r['rho_exo_c']:.3f}")
