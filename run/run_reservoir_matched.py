import pickle, json, time
from model_core import run_pooled
from load_reservoir import EXO
c=pickle.load(open("data/reservoir_matched_cache.pkl","rb"))
t=time.time()
r=run_pooled("Reservoir(ASOS-matched)", c["frames"], "D", 7, EXO, subsample_origin=14, n_est=200)
print(f"    {time.time()-t:.0f}s")
r["assign"]=c["assign"]
json.dump(r, open("out/rho_reservoir_matched.json","w"), indent=2)
# print side-by-side vs network-average
net={x["domain"]:x for x in json.load(open("out/rho_B.json"))}["Reservoir(ASOS-net)"]
print("\n           persist_share  rho_endo_c  rho_exo_c  |  CRPS_clim  CRPS_persist  CRPS_hist  CRPS_full")
for tag,x in [("network-avg",net),("per-reservoir",r)]:
    print(f"{tag:14s} {x['persist_share']:.3f}       {x['rho_endo_c']:.3f}     {x['rho_exo_c']:.3f}   |  "
          f"{x['CRPS_clim']:.4f}    {x['CRPS_persist']:.4f}     {x['CRPS_hist']:.4f}    {x['CRPS_full']:.4f}")
