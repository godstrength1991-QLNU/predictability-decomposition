"""HKUST subtropical rooftop PV (forcing pole). Single campus weather station (shared exo),
60 PV site series. Everything aggregated to DAILY. Target = daily-mean power (W)."""
import zipfile, io, numpy as np, pandas as pd
ZIP="data/hkust/Dataset.zip"
MET={"Irradiance":"rad","Rainfall":"precip","Relative Humidity":"rh",
     "Sea Level Pressure":"pres","Temperature":"temp","Visibility":"vis","Wind":"wind"}
EXO=list(MET.values())

def _read_any(z, name):
    with z.open(name) as f:
        raw=f.read()
    if name.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(raw))
    return pd.read_csv(io.BytesIO(raw))

def load_meteo_daily():
    z=zipfile.ZipFile(ZIP); names=z.namelist()
    daily={}
    for folder,code in MET.items():
        parts=[]
        for n in [x for x in names if f"Meteorological dataset/{folder}/" in x and (x.endswith(".csv") or x.endswith(".xlsx"))]:
            df=_read_any(z,n)
            t=pd.to_datetime(df.iloc[:,0], errors="coerce")
            v=pd.to_numeric(df.iloc[:,1], errors="coerce")     # col1 = primary value
            parts.append(pd.Series(v.values, index=t).dropna())
        s=pd.concat(parts).sort_index()
        agg = s.resample("D").sum() if code=="precip" else s.resample("D").mean()
        daily[code]=agg
    return pd.DataFrame(daily)

def load_pv_frames(n_sites=20):
    z=zipfile.ZipFile(ZIP); names=z.namelist()
    site=[n for n in names if "PV generation dataset" in n and "Site level" in n and n.endswith(".csv")]
    site=sorted(site)[:n_sites]
    met=load_meteo_daily()
    frames=[]; used=[]
    for n in site:
        df=_read_any(z,n)
        t=pd.to_datetime(df.iloc[:,0], errors="coerce")
        pw=pd.to_numeric(df["power(W)"] if "power(W)" in df.columns else df.iloc[:,-1], errors="coerce")
        y=pd.Series(pw.values,index=t).dropna().clip(lower=0).resample("D").mean()
        if y.notna().sum()<200: continue
        fr=pd.DataFrame(index=y.index); fr["y"]=y
        m=met.reindex(y.index)
        for c in EXO: fr[c]=m[c].values
        frames.append(fr.dropna(subset=["y"])); used.append(n.split("/")[-1])
    return frames, met, used

if __name__=="__main__":
    import pickle
    met=load_meteo_daily()
    print("meteo daily:",met.index.min().date(),"..",met.index.max().date(),"n=",len(met))
    print(met.describe().round(2).T[["mean","min","max"]])
    frames,met,used=load_pv_frames(20)
    print(f"\n{len(frames)} PV site frames; first={used[0]} y~{frames[0]['y'].mean():.0f}W n={frames[0]['y'].notna().sum()}")
    pickle.dump({"frames":frames}, open("data/hkust_cache.pkl","wb"))
    print("cached data/hkust_cache.pkl")
