import pickle, json, time
from model_core import run_pooled
from load_reservoir import EXO
c=pickle.load(open("data/reservoir_full_cache.pkl","rb"))
t=time.time()
r=run_pooled("Reservoir(full-403 matched)", c["frames"], "D", 7, EXO, subsample_origin=200, n_est=200)
r["n_dams"]=len(c["frames"]); r["note"]="full 403 dams, ASOS per-reservoir matched, stride~200d"
print(f"    {time.time()-t:.0f}s ({len(c['frames'])} dams)")
json.dump(r, open("out/rho_reservoir_full.json","w"), indent=2)
m=json.load(open("out/rho_reservoir_matched.json"))
print("\n                    persist_share  rho_endo_c  rho_exo_c   (n_test)")
print(f"25 dams (stride14)   {m['persist_share']:.3f}       {m['rho_endo_c']:.3f}     {m['rho_exo_c']:.3f}    {m['n_test']:,}")
print(f"403 dams(stride200)  {r['persist_share']:.3f}       {r['rho_endo_c']:.3f}     {r['rho_exo_c']:.3f}    {r['n_test']:,}")
