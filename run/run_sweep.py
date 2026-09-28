import pickle, json, sys, os, time
from model_core import run_pooled
from load_camels import EXO
c=pickle.load(open("data/camels/camels_cache.pkl","rb"))
frames=c["frames"][::5]                                  # ~18 basins
path="out/camels_sweep.json"
res=json.load(open(path)) if os.path.exists(path) else []
for H in [int(x) for x in sys.argv[1:]]:
    t=time.time()
    r=run_pooled(f"CAMELS_H{H}", frames, "D", H, EXO, subsample_origin=45, n_est=150)
    res=[x for x in res if x["H"]!=H]+[{"H":H,"rho_endo_c":r["rho_endo_c"],"rho_exo_c":r["rho_exo_c"],
        "persist_share":r["persist_share"],"n_test":r["n_test"]}]
    print(f"    H={H} {time.time()-t:.0f}s")
json.dump(sorted(res,key=lambda x:x["H"]), open(path,"w"), indent=2)
