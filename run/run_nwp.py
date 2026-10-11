"""Value of real NWP forecasts (perfect-prognosis design). Models are trained on observed
forcing before 2024-04-01; on the test period (2024-04-01 to 2025-08) the future forcing is
either observed (perfect forecast) or replaced by the archived ECMWF/GFS forecast issued
k days ahead (Open-Meteo Previous Runs API), aggregated to local days exactly like the
observations (UTC+9:30; daily means, precipitation daily total)."""
import pickle, json, sys, numpy as np, pandas as pd
import model_core as M, dkasc_rc, load_dkasc as L
from model_core import build_samples, _fit_predict_crps
MAP_ALL={"Global_Horizontal_Radiation":"shortwave_radiation","Diffuse_Horizontal_Radiation":"diffuse_radiation",
     "Weather_Temperature_Celsius":"temperature_2m","Weather_Relative_Humidity":"relative_humidity_2m",
     "Wind_Speed":"wind_speed_10m","Weather_Daily_Rainfall":"precipitation"}
MAP={k:v for k,v in MAP_ALL.items() if k!="Wind_Speed"}
EXO=list(MAP)
NWP=pickle.load(open("data/nwp/nwp_dkasc.pkl","rb"))
def daily_nwp(df):
    loc=df.copy(); loc.index=loc.index+pd.Timedelta(hours=9,minutes=30)
    g=loc.groupby(loc.index.floor("D")); out={}
    for obs,v in MAP.items():
        for k in range(1,8):
            c=f"{v}_previous_day{k}"
            agg=g[c].sum(min_count=20) if v=="precipitation" else g[c].mean()
            out[(obs,k)]=agg.where(g[c].count()>=20)        # require >=20 of 24 hours
    return out

def bias_correct(V, long, te, fut, leads):
    """Linear correction obs = a + b*forecast per variable and lead, cross-fitted by calendar
    month: each month is corrected with coefficients estimated on the other months only
    (forcing variables only; the target is never used)."""
    W=V.copy(); month=long["tdate"].dt.to_period("M").values; O=long[fut].values.astype(float)
    for j in range(V.shape[1]):
        for k in range(1,8):
            rows=np.where(te&(leads==k))[0]
            for mth in np.unique(month[rows]):
                fit=rows[month[rows]!=mth]; app=rows[month[rows]==mth]
                x,y=V[fit,j],O[fit,j]; g=~(np.isnan(x)|np.isnan(y))
                if g.sum()<30: continue
                b,a=np.polyfit(x[g],y[g],1); W[app,j]=a+b*V[app,j]
    return W

site=sys.argv[1]; T0=pd.Timestamp("2024-04-01")
d=dkasc_rc.load(site,"D"); long,feats=build_samples(d,"D",7,EXO)
long["tdate"]=long["origin"]+pd.to_timedelta(long["lead"],unit="D")
tr=(long["origin"]<=T0-pd.Timedelta(7,"D")).values
te0=((long["origin"]>=T0)&(long["tdate"]<=d.index.max())).values
models={m:daily_nwp(NWP[m]) for m in ["ecmwf","gfs"]}
# rows usable for BOTH models (identical test set for every configuration)
ok=te0.copy()
nwp_vals={}
for m,dd in models.items():
    V=np.full((len(long),len(MAP)),np.nan)
    for j,obs in enumerate(MAP):
        for k in range(1,8):
            sel=(long["lead"]==k).values&te0
            V[sel,j]=dd[(obs,k)].reindex(long.loc[sel,"tdate"]).values
    nwp_vals[m]=V; ok&=~np.isnan(V).any(1)
fut=[f"fut_{o}" for o in MAP]
ok&=~long[fut].isna().any(axis=1).values      # observed forcing also complete
te=ok
C={c:_fit_predict_crps(long,feats[c],tr,te,n_est=150) for c in ["clim","hist","full"]}
fut=[f"fut_{o}" for o in MAP]
leads_all=long["lead"].values
for m,V in nwp_vals.items():
    for tag,VV in [("",V),("_bc",bias_correct(V,long,te,fut,leads_all))]:
        L2=long.copy(); L2.loc[te,fut]=VV[te].astype(L2[fut[0]].dtype)
        C["full_"+m+tag]=_fit_predict_crps(L2,feats["full"],tr,te,n_est=150)
lead=long.loc[te,"lead"].values
def rho(mask):
    cl=C["clim"][mask].mean(); h=C["hist"][mask].mean()
    r={"rho_endo":(cl-h)/cl,"rho_exo_perfect":(h-C["full"][mask].mean())/cl}
    for m in nwp_vals:
        for tag in ["","_bc"]:
            r[f"rho_exo_{m}{tag}"]=(h-C["full_"+m+tag][mask].mean())/cl
            r[f"retained_{m}{tag}"]=r[f"rho_exo_{m}{tag}"]/r["rho_exo_perfect"]
    return r
allr=rho(np.ones(te.sum(),bool)); bylead={int(k):rho(lead==k) for k in range(1,8)}
res={"site":site,"n_test":int(te.sum()),"test_period":[str(long.loc[te,"origin"].min().date()),str(long.loc[te,"tdate"].max().date())],
     "n_train":int(tr.sum()),"all_leads":allr,"by_lead":bylead}
json.dump(res,open(f"out/nwp_{site}.json","w"),indent=2)
print(f"{site}: n_test={res['n_test']} {res['test_period']}")
print("  all leads:",{k:round(v,3) for k,v in allr.items()})
print("  lead | perfect | retained: ECMWF raw  ECMWF bc | GFS raw  GFS bc")
for k,r in bylead.items(): print(f"   {k}   |  {r['rho_exo_perfect']:.3f}  |        {r['retained_ecmwf']:5.0%}     {r['retained_ecmwf_bc']:5.0%}  |  {r['retained_gfs']:5.0%}   {r['retained_gfs_bc']:5.0%}")
