import pickle, json, time
from model_core import run_domain
from load_dkasc import EXO
store = pickle.load(open("data/dkasc_cache.pkl","rb"))
res=[]
print("===== Horizon B: daily, H=7 =====")
for s in store:
    t=time.time(); res.append(run_domain(s, store[s]["daily"], "D", 7, EXO)); print(f"    {time.time()-t:.0f}s")
json.dump(res, open("out/rho_horizonB.json","w"), indent=2)
print("saved out/rho_horizonB.json")
