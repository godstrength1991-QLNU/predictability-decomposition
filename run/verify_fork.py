import pickle, json
from model_core import run_pooled, run_domain
from load_reservoir import EXO as REXO
from load_dkasc import EXO as DEXO
c=pickle.load(open("data/reservoir_cache.pkl","rb"))
r_res=run_pooled("Reservoir(ASOS-net)", c["frames"], "D", 7, REXO, subsample_origin=14, n_est=200)
st=pickle.load(open("data/dkasc_cache.pkl","rb"))
r_s13=run_domain("DKASC_site13", st["DKASC_site13"]["daily"], "D", 7, DEXO, n_est=200)
json.dump([r_res,r_s13], open("out/fork_check.json","w"), indent=2)
