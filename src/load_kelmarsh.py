"""Kelmarsh wind farm (forcing pole). Target = Power (kW) per turbine.
Exogenous forcing = wind speed + ambient temperature (future wind = oracle).
Raw 10-min per-turbine CSV -> daily. 6 turbines pooled (each has own anemometer)."""
import zipfile, io, os, glob, numpy as np, pandas as pd
UP="data/kelmarsh"
TS="# Date and time"; POW="Power (kW)"; WS="Wind speed (m/s)"; TMP="Nacelle ambient temperature (°C)"
USE=[TS,POW,WS,TMP]
EXO=["wind","temp"]

def _read_turbine_year(zf, member):
    with zipfile.ZipFile(zf) as z, z.open(member) as f:
        df=pd.read_csv(io.BytesIO(f.read()), skiprows=9, usecols=USE,
                       dtype={POW:"float32",WS:"float32",TMP:"float32"})
    df["t"]=pd.to_datetime(df[TS], errors="coerce")
    df=df.dropna(subset=["t"]).set_index("t").sort_index()
    df=df.rename(columns={POW:"y",WS:"wind",TMP:"temp"})
    df["y"]=df["y"].clip(lower=0)                       # ignore idling consumption
    df.loc[df["wind"]<0,"wind"]=np.nan
    df.loc[(df["temp"]<-40)|(df["temp"]>55),"temp"]=np.nan
    return df[["y","wind","temp"]]

def _daily(df):
    exp=24*6                                            # 10-min slots/day
    g=df.groupby(df.index.normalize())
    cov=g["y"].count()/exp
    out=pd.DataFrame(index=cov.index)
    out["y"]=g["y"].mean()
    for c in EXO: out[c]=g[c].mean()
    return out[cov>=0.8].dropna(subset=["y"])

if __name__=="__main__":
    import time
    zf=f"{UP}/Kelmarsh_SCADA_2021_4456.zip"
    m="Turbine_Data_Kelmarsh_1_2021-01-01_-_2022-01-01_228.csv"
    t=time.time(); df=_read_turbine_year(zf,m); print(f"read {len(df):,} rows in {time.time()-t:.0f}s")
    d=_daily(df); print("daily:",d.index.min().date(),"..",d.index.max().date(),"n=",len(d))
    print(d.describe().round(2).T[["mean","min","max"]])
