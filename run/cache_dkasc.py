import pickle, time
from load_dkasc import load_site, SITES
store={}
for s in SITES:
    t=time.time(); d,h=load_site(s); store[s]={"daily":d,"hourly":h}
    print(f"    cached in {time.time()-t:.0f}s\n")
pickle.dump(store, open("data/dkasc_cache.pkl","wb"))
print("saved data/dkasc_cache.pkl")
