import pickle, json, time
from model_core import run_pooled
from load_kelmarsh import EXO
c=pickle.load(open("data/kelmarsh_cache.pkl","rb"))
t=time.time()
r=run_pooled("Kelmarsh(wind)", c["frames"], "D", 7, EXO, n_est=200)
r["n_turbines"]=len(c["frames"]); r["note"]="6 turbines, 2019-2022, daily"
print(f"    {time.time()-t:.0f}s")
json.dump(r, open("out/rho_kelmarsh.json","w"), indent=2)
