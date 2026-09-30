"""Drift-corrected DKASC targets. Plant capacity changes (inverter outages, degradation)
are removed by dividing output by a trailing 90-day 99th percentile of the same series
(past data only, lagged one step). Rows without a valid capacity estimate are dropped."""
import pickle
WIN={"D":90,"h":90*24}; MINP={"D":60,"h":60*24}
def load(site, freq="D", cache="data/dkasc_cache.pkl"):
    d=pickle.load(open(cache,"rb"))[site]["daily" if freq=="D" else "hourly"].copy()
    cap=d["y"].rolling(WIN[freq],min_periods=MINP[freq]).quantile(0.99).shift(1)
    d["y"]=d["y"]/cap
    return d[cap.notna()&(cap>0)]
