"""Scheme-2: per-reservoir ASOS matching. Each reservoir uses its NEAREST ASOS station's
daily meteorology (not the province network average). Station location is derived reproducibly
from the data: centroid of reservoirs in the station's eponymous district (sigungu). Missing
station-days fall back to the network average so the oracle stays populated."""
import pickle, glob, numpy as np, pandas as pd
from load_reservoir import ASOS_VARS, EXO
RES="data/reservoir"

def _norm(name):   # strip trailing 시/군 for name matching
    return name[:-1] if name and name[-1] in "시군" else name

def load_asos_per_station():
    frames=[]
    for f in sorted(glob.glob(f"{RES}/ASOS_weather_*.csv")):
        df=pd.read_csv(f, encoding="cp949", usecols=["지점명","일시"]+list(ASOS_VARS))
        df=df.rename(columns={"일시":"date","지점명":"stn",**ASOS_VARS})
        df["date"]=pd.to_datetime(df["date"], errors="coerce"); df["stn"]=df["stn"].map(_norm)
        frames.append(df)
    a=pd.concat(frames, ignore_index=True).dropna(subset=["date"])
    net=a.groupby("date")[EXO].mean()                       # network average (fallback)
    per={s: g.groupby("date")[EXO].mean().sort_index() for s,g in a.groupby("stn")}
    return per, net

def build_matched_frames(n_res=25):
    d=pickle.load(open(f"{RES}/mawp_dataset.pkl","rb"))
    dates=pd.to_datetime(d["dates"].astype(str))
    sr=np.clip(d["storage_rate"],0,1); loc=d["locations"]; sig=np.array([_norm(s) for s in d["sigungu"]])
    per,net=load_asos_per_station()
    stns=sorted(per.keys())
    # station location = centroid of reservoirs in its eponymous district
    cent={}
    for s in stns:
        m=sig==s
        if m.sum()>0: cent[s]=loc[m].mean(axis=0)
    cstn=[s for s in stns if s in cent]
    C=np.array([cent[s] for s in cstn])
    def nearest(latlon):
        dlat=np.radians(C[:,0]-latlon[0]); dlon=np.radians(C[:,1]-latlon[1])
        a=np.sin(dlat/2)**2+np.cos(np.radians(latlon[0]))*np.cos(np.radians(C[:,0]))*np.sin(dlon/2)**2
        return cstn[int(np.argmin(2*np.arctan2(np.sqrt(a),np.sqrt(1-a))))]
    idx=np.linspace(0,sr.shape[0]-1,n_res).astype(int)
    frames=[]; assign={}
    for r in idx:
        st=nearest(loc[r]); assign[st]=assign.get(st,0)+1
        exo=per[st].reindex(dates)
        exo=exo.fillna(net.reindex(dates))                  # fallback to network avg on missing days
        fr=pd.DataFrame(index=dates); fr["y"]=sr[r]
        for c in EXO: fr[c]=exo[c].values
        frames.append(fr.dropna(subset=["y"]))
    return frames, idx, assign, cstn

if __name__=="__main__":
    per,net=load_asos_per_station()
    print("per-station coverage:")
    for s in sorted(per): print(f"  {s}: {per[s].index.min().date()}..{per[s].index.max().date()} n={len(per[s])}")
    frames,idx,assign,cstn=build_matched_frames(25)
    print("\nstation centroids used:",cstn)
    print("assignment of the 25 sampled reservoirs -> station:",assign)
    pickle.dump({"frames":frames,"idx":idx,"assign":assign}, open("data/reservoir_matched_cache.pkl","wb"))
    print("cached data/reservoir_matched_cache.pkl")
