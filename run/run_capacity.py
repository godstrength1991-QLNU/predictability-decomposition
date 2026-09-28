import pickle, json, sys, time
import model_core as M
from model_core import run_pooled, run_domain
dom=sys.argv[1]
caps=[("weak",50,8),("medium",150,31),("strong",400,63)]
out=[]
for name,trees,leaves in caps:
    M.LGB["num_leaves"]=leaves; t=time.time()
    if dom=="reservoir":
        import load_reservoir as L; c=pickle.load(open("data/reservoir_full_cache.pkl","rb"))
        r=run_pooled(f"Reservoir[{name}]", c["frames"], "D",7, L.EXO, subsample_origin=700, n_est=trees)
    elif dom=="kelmarsh":
        import load_kelmarsh as L; c=pickle.load(open("data/kelmarsh_cache.pkl","rb"))
        r=run_pooled(f"Kelmarsh[{name}]", c["frames"], "D",7, L.EXO, n_est=trees)
    elif dom=="M9":
        import load_dkasc as L; st=pickle.load(open("data/dkasc_cache.pkl","rb"))
        r=run_domain(f"M9[{name}]", st["DKASC_M9"]["daily"], "D",7, L.EXO, n_est=trees)
    out.append({"cap":name,"trees":trees,"leaves":leaves,
                "rho_endo_c":round(r["rho_endo_c"],3),"rho_exo_c":round(r["rho_exo_c"],3)})
    print(f"    {name} {time.time()-t:.0f}s")
M.LGB["num_leaves"]=31
json.dump(out, open(f"out/cap_{dom}.json","w"), indent=2)
