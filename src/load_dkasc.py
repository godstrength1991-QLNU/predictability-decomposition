"""DKASC loader: raw 5-min CSV -> unified daily & hourly frames.
Unified schema: target 'y' + exogenous forcing cols + DatetimeIndex.
Sanitises sensor sentinels and trims non-operational (all-zero) commissioning stretches.
"""
import numpy as np, pandas as pd, zipfile, os

UP = "data/dkasc"
SITES = {
    "DKASC_site13": ("archive.zip",   "92-Site_DKA-M6_B-Phase-site13.csv"),
    "DKASC_site31": ("archive__1_.zip","74-Site_DKA-M18_C-Phase-site31.csv"),
    "DKASC_M9":     ("archive__2_.zip","87-Site_DKA-M9_AC-Phases.csv"),
}
USE = ["timestamp","Active_Power",
       "Global_Horizontal_Radiation","Diffuse_Horizontal_Radiation",
       "Weather_Temperature_Celsius","Weather_Relative_Humidity",
       "Wind_Speed","Weather_Daily_Rainfall"]          # dropped Wind_Direction (sentinel-heavy, minor for PV)
EXO = ["Global_Horizontal_Radiation","Diffuse_Horizontal_Radiation",
       "Weather_Temperature_Celsius","Weather_Relative_Humidity",
       "Wind_Speed","Weather_Daily_Rainfall"]

def _read_raw(zf, csv, name=''):
    kw = dict(usecols=USE, dtype={c:"float32" for c in USE if c!="timestamp"})
    with zipfile.ZipFile(os.path.join(UP,zf)) as z:
        try:
            with z.open(csv) as f:
                df = pd.read_csv(f, **kw)
        except Exception as e:
            print(f"  [robust-read fallback: {type(e).__name__}] {name}")
            with z.open(csv) as f:
                df = pd.read_csv(f, engine="python", on_bad_lines="skip", **kw)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()
    # ---- sanitise sentinels / impossible values -> NaN (radiation/power neg -> 0) ----
    df["Active_Power"] = df["Active_Power"].clip(lower=0)
    for c in ["Global_Horizontal_Radiation","Diffuse_Horizontal_Radiation"]:
        df[c] = df[c].clip(lower=0)
    df.loc[(df["Weather_Temperature_Celsius"]<-20)|(df["Weather_Temperature_Celsius"]>55),
           "Weather_Temperature_Celsius"] = np.nan
    df["Weather_Relative_Humidity"] = df["Weather_Relative_Humidity"].clip(0,100)
    df.loc[df["Wind_Speed"]<0,"Wind_Speed"] = np.nan
    df.loc[df["Weather_Daily_Rainfall"]<0,"Weather_Daily_Rainfall"] = 0
    return df

def _agg(raw, freq, floor):
    step = raw.index.to_series().diff().dt.total_seconds().median()/60
    exp = (24*60 if freq=="D" else 60)/step
    key = raw.index.normalize() if freq=="D" else raw.index.floor("h")
    g = raw.groupby(key)
    cov = g["Active_Power"].count()/exp
    out = pd.DataFrame(index=cov.index)
    out["y"] = g["Active_Power"].mean()
    for c in EXO:
        out[c] = g[c].max() if c=="Weather_Daily_Rainfall" else g[c].mean()
    out = out[cov>=0.8].dropna(subset=["y"]).asfreq(freq)
    return out, step

def _trim_commissioning(daily):
    # keep from first date where 14-day rolling median output is clearly operational
    med = daily["y"].rolling(14,min_periods=7).median()
    thr = 0.10*daily["y"].median()
    ok = med[med>thr]
    if len(ok):
        start = ok.index[0]; daily = daily[daily.index>=start]
    return daily

def load_site(name, verbose=True):
    zf,csv = SITES[name]; raw=_read_raw(zf,csv,name); n0=len(raw)
    daily,step = _agg(raw,"D","D"); hourly,_ = _agg(raw,"h","h")
    daily = _trim_commissioning(daily)
    hourly = hourly[hourly.index>=daily.index.min()]
    if verbose:
        print(f"[{name}] ~{step:.0f}min raw={n0:,} | daily {daily.index.min().date()}..{daily.index.max().date()} "
              f"n={daily['y'].notna().sum()} ymean={daily['y'].mean():.2f} | hourly n={hourly['y'].notna().sum()}")
    del raw
    return daily, hourly

if __name__=="__main__":
    for s in SITES:
        d,h = load_site(s)
    print("\nsite13 daily exo ranges (post-clean):")
    d,h = load_site("DKASC_site13",verbose=False)
    print(d.describe().round(2).T[["mean","min","max"]])
