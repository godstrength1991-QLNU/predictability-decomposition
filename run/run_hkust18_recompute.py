import pickle, json, numpy as np
import model_core as M
M.QLEVELS=np.round(np.arange(0.05,0.96,0.05),3)   # 19 levels: same configuration as the other robustness rows
from model_core import run_pooled
from load_hkust import EXO
c=pickle.load(open("data/hkust_cache.pkl","rb"))
r=run_pooled("HKUST(18 sites)", c["frames"], "D",7, EXO, subsample_origin=2, n_est=200)
r["n_sites"]=len(c["frames"]); r["config"]="19 quantiles, 200 trees, origin stride 2"
json.dump(r, open("out/rho_hkust_18.json","w"), indent=2)
