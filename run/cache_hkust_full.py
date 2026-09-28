import pickle, time
from load_hkust import load_pv_frames
t=time.time()
frames, met, used = load_pv_frames(n_sites=60)
print(f"loaded {len(frames)} PV site frames in {time.time()-t:.0f}s")
pickle.dump({"frames":frames}, open("data/hkust_cache_full.pkl","wb"))
print("cached data/hkust_cache_full.pkl")
