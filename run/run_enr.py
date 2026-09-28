import pickle, json, sys, time
from model_core import run_pooled_enriched, run_domain_enriched
which=sys.argv[1]
t=time.time()
if which=="reservoir":
    import load_reservoir as L
    c=pickle.load(open("data/reservoir_full_cache.pkl","rb"))
    r=run_pooled_enriched("Reservoir(ASOS-net)", c["frames"], "D",7, L.EXO, subsample_origin=200, n_est=150)
elif which=="camels":
    import load_camels as L
    c=pickle.load(open("data/camels/camels_cache.pkl","rb"))
    r=run_pooled_enriched("CAMELS(streamflow)", c["frames"][::2], "D",7, L.EXO, subsample_origin=21, n_est=150)
elif which=="hkust":
    import load_hkust as L
    c=pickle.load(open("data/hkust_cache_full.pkl","rb"))
    r=run_pooled_enriched("HKUST(subtropical PV)", c["frames"], "D",7, L.EXO, subsample_origin=2, n_est=150)
else:  # DKASC site, horizon B
    import load_dkasc as L
    st=pickle.load(open("data/dkasc_cache.pkl","rb"))
    r=run_domain_enriched(which, st[which]["daily"], "D",7, L.EXO, n_est=150)
json.dump(r, open(f"out/enr_{which}.json","w"), indent=2)
print(f"  {time.time()-t:.0f}s -> out/enr_{which}.json")
