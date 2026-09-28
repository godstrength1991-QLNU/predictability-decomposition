import pickle, time
from load_reservoir_matched import build_matched_frames
t=time.time()
frames, idx, assign, cstn = build_matched_frames(n_res=403)   # ALL dams
print(f"built {len(frames)} matched reservoir frames in {time.time()-t:.0f}s")
print("station assignment over all 403 dams:", dict(sorted(assign.items(), key=lambda x:-x[1])))
pickle.dump({"frames":frames,"assign":assign}, open("data/reservoir_full_cache.pkl","wb"))
print("cached data/reservoir_full_cache.pkl")
