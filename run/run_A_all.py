import pickle, json
from model_core import run_domain
from load_dkasc import EXO
st=pickle.load(open("data/dkasc_cache.pkl","rb"))
res=[]
for s in ["DKASC_site13","DKASC_site31","DKASC_M9"]:
    res.append(run_domain(s, st[s]["hourly"], "h", 24, EXO,
                          daytime_only=True, subsample_origin=72, n_est=200))
json.dump(res, open("out/rho_A.json","w"), indent=2)
print("saved out/rho_A.json")
