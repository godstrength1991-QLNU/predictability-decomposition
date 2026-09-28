"""Reservoir domain (inertia pole). Target = storage_rate (0-1) per reservoir.
Exogenous forcing = network-average ASOS daily meteorology (Scheme 1, shared across reservoirs).
"""
import pickle, glob, numpy as np, pandas as pd, os
RES="data/reservoir"
ASOS_VARS = {   # Korean name -> short code
 "평균기온(°C)":"temp", "일강수량(mm)":"precip", "평균 풍속(m/s)":"wind",
 "평균 상대습도(%)":"rh", "평균 현지기압(hPa)":"pres", "합계 일조시간(hr)":"sun",
 "합계 일사량(MJ/m2)":"rad", "평균 전운량(1/10)":"cloud", "합계 소형증발량(mm)":"evap"}
EXO = list(ASOS_VARS.values())

def load_asos_network():
    frames=[]
    for f in sorted(glob.glob(f"{RES}/ASOS_weather_*.csv")):
        df=pd.read_csv(f, encoding="cp949", usecols=["일시"]+list(ASOS_VARS))
        df=df.rename(columns={"일시":"date",**ASOS_VARS})
        df["date"]=pd.to_datetime(df["date"], errors="coerce")
        frames.append(df)
    a=pd.concat(frames, ignore_index=True).dropna(subset=["date"])
    net=a.groupby("date")[EXO].mean().sort_index()      # network average across stations
    return net

def load_reservoir_frames(n_res=25, seed=0):
    d=pickle.load(open(f"{RES}/mawp_dataset.pkl","rb"))
    dates=pd.to_datetime(d["dates"].astype(str))
    sr=np.clip(d["storage_rate"],0,1)                   # (403,10958)
    net=load_asos_network().reindex(dates)              # align ASOS to reservoir dates
    idx=np.linspace(0,sr.shape[0]-1,n_res).astype(int)  # spread across 403
    frames=[]
    for r in idx:
        fr=pd.DataFrame(index=dates); fr.index.name="date"
        fr["y"]=sr[r]
        for c in EXO: fr[c]=net[c].values
        frames.append(fr.dropna(subset=["y"]))
    return frames, idx

if __name__=="__main__":
    net=load_asos_network()
    print("ASOS net:", net.index.min().date(),"..",net.index.max().date(),"n=",len(net))
    print(net.describe().round(2).T[["mean","min","max"]])
    frames,idx=load_reservoir_frames(25)
    print(f"\n{len(frames)} reservoir frames; example y range "
          f"{frames[0]['y'].min():.2f}..{frames[0]['y'].max():.2f}, n={frames[0]['y'].notna().sum()}")
    pickle.dump({"frames":frames,"idx":idx}, open("data/reservoir_cache.pkl","wb"))
    print("cached data/reservoir_cache.pkl")
