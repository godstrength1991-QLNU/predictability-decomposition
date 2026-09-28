import zipfile, glob, re, time, pickle, pandas as pd
from load_kelmarsh import _read_turbine_year, _daily, UP
zips=sorted(glob.glob(f"{UP}/Kelmarsh_SCADA_*.zip"))
per={n:[] for n in range(1,7)}
t0=time.time()
for zf in zips:
    with zipfile.ZipFile(zf) as z:
        members=[m for m in z.namelist() if m.startswith("Turbine_Data_Kelmarsh_")]
    for m in members:
        n=int(re.search(r"Turbine_Data_Kelmarsh_(\d)_",m).group(1))
        d=_daily(_read_turbine_year(zf,m))
        per[n].append(d)
    print(f"  {zf.split('/')[-1]} done ({time.time()-t0:.0f}s)")
frames=[]
for n in range(1,7):
    fr=pd.concat(per[n]).sort_index()
    fr=fr[~fr.index.duplicated()]
    frames.append(fr)
    print(f"Turbine {n}: {fr.index.min().date()}..{fr.index.max().date()} n={len(fr)} y_mean={fr['y'].mean():.0f}kW")
pickle.dump({"frames":frames}, open("data/kelmarsh_cache.pkl","wb"))
print(f"cached {len(frames)} turbine frames in {time.time()-t0:.0f}s")
