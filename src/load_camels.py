"""CAMELS streamflow (intermediate pole: storage/baseflow inertia + rainfall forcing).
Target y = observed discharge converted cfs -> mm/day (via basin area).
Exogenous forcing = Daymet prcp/srad/tmax/tmin/vp (future forcing = oracle)."""
import glob, os, numpy as np, pandas as pd
CAM="data/camels"
EXO=["prcp","srad","tmax","tmin","vp"]
CFS_TO_MMDAY=0.0283168466*86400*1000.0                 # * (1/area_m2)

def parse_forcing(path):
    with open(path) as f:
        f.readline(); f.readline(); area=float(f.readline())   # line3 = area m^2
    df=pd.read_csv(path, skiprows=3, sep=r"\s+")
    df.columns=[c.split("(")[0].strip().lower() for c in df.columns]  # dayl,prcp,srad,swe,tmax,tmin,vp
    df["date"]=pd.to_datetime(dict(year=df["year"],month=df["mnth"],day=df["day"]))
    df=df.set_index("date")[["prcp","srad","tmax","tmin","vp"]].astype("float32")
    return df, area

def parse_streamflow(path, area):
    df=pd.read_csv(path, sep=r"\s+", header=None,
                   names=["id","year","mnth","day","q","qc"])
    df["date"]=pd.to_datetime(dict(year=df["year"],month=df["mnth"],day=df["day"]))
    q=df["q"].astype("float32").to_numpy(copy=True)
    q[q<0]=np.nan                                       # -999 = missing
    y=pd.Series(q*(CFS_TO_MMDAY/area), index=df["date"], name="y")
    return y

def build_frames(max_basins=None):
    fcs={os.path.basename(p).split("_")[0]:p for p in glob.glob(f"{CAM}/forcing/03/*_forcing_leap.txt")}
    sfs={os.path.basename(p).split("_")[0]:p for p in glob.glob(f"{CAM}/streamflow/03/*_streamflow_qc.txt")}
    gauges=sorted(set(fcs)&set(sfs))
    if max_basins: gauges=gauges[::max(1,len(gauges)//max_basins)][:max_basins]
    frames=[]
    for g in gauges:
        fdf,area=parse_forcing(fcs[g]); y=parse_streamflow(sfs[g],area)
        fr=fdf.join(y,how="inner"); fr=fr.dropna(subset=["y"])
        if len(fr)>2000: frames.append(fr)
    return frames, gauges

if __name__=="__main__":
    import pickle
    frames,gauges=build_frames()
    print(f"paired basins: {len(gauges)}, usable frames (>2000 days): {len(frames)}")
    f0=frames[0]
    print("example:", f0.index.min().date(),"..",f0.index.max().date(),"n=",len(f0))
    print(f0[["y"]+EXO].describe().round(2).T[["mean","min","max"]])
    pickle.dump({"frames":frames}, open(f"{CAM}/camels_cache.pkl","wb"))
    print("cached", f"{CAM}/camels_cache.pkl")
