import pickle, json, time
from model_core import run_pooled
from load_camels import EXO
c=pickle.load(open("data/camels/camels_cache.pkl","rb"))
frames=c["frames"][::2]                                 # ~46 basins
t=time.time()
r=run_pooled("CAMELS(streamflow)", frames, "D", 7, EXO, subsample_origin=21, n_est=200)
r["n_basins"]=len(frames); r["note"]="HUC03, ~46 basins, 1980-2014, 3-week origin stride"
print(f"    {time.time()-t:.0f}s ({len(frames)} basins)")
json.dump(r, open("out/rho_camels.json","w"), indent=2)
