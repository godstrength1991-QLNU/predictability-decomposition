"""Normalised permutation entropy (Bandt & Pompe 2002) of each domain's daily target
series, compared with the decomposition coefficients. Order d = 4, delay 1; windows
containing missing values are skipped. Per domain: median over series."""
import pickle, json, math, itertools, numpy as np
from scipy.stats import spearmanr
def pe(x, d=4):
    x=np.asarray(x,float); n=len(x)-d+1
    if n<50: return np.nan
    W=np.lib.stride_tricks.sliding_window_view(x,d)
    W=W[~np.isnan(W).any(1)]
    if len(W)<50: return np.nan
    W=W+1e-12*np.arange(d)                       # deterministic tie-breaking
    pats=np.argsort(W,axis=1); keys=(pats*(d**np.arange(d))).sum(1)
    _,cnt=np.unique(keys,return_counts=True); p=cnt/cnt.sum()
    return float(-(p*np.log(p)).sum()/math.log(math.factorial(d)))
def dom_pe(frames): 
    v=[pe(f["y"].values) for f in frames]; v=[x for x in v if not np.isnan(x)]
    return float(np.median(v)), len(v)
out={}
res=pickle.load(open("data/reservoir_full_cache.pkl","rb"))["frames"]
out["Reservoir(ASOS-net)"]=dom_pe(res)
out["CAMELS(streamflow)"]=dom_pe(pickle.load(open("data/camels/camels_cache.pkl","rb"))["frames"][::2])
import dkasc_rc
for s in ["DKASC_site13","DKASC_site31","DKASC_M9"]: out[s]=dom_pe([dkasc_rc.load(s,"D")])
hk=pickle.load(open("data/hkust_cache_full.pkl","rb"))["frames"]; out["HKUST(subtropical PV)"]=dom_pe(hk)
out["Kelmarsh(wind)"]=dom_pe(pickle.load(open("data/kelmarsh_cache.pkl","rb"))["frames"])
B={r["domain"]:r for r in json.load(open("out/rho_B.json"))}
rows=[]
for k,(v,n) in out.items():
    b=B[k]; rows.append(dict(domain=k,PE=round(v,3),n_series=n,rho_endo=round(b["rho_endo_c"],3),
        rho_exo=round(b["rho_exo_c"],3),rho_tot=round(b["rho_endo_c"]+b["rho_exo_c"],3)))
for r in rows: print(f"{r['domain']:24s} PE={r['PE']:.3f} (n={r['n_series']})  endo={r['rho_endo']:.2f} exo={r['rho_exo']:.2f} tot={r['rho_tot']:.2f}")
pe_=[r["PE"] for r in rows]
sp={k:round(spearmanr(pe_,[r[k] for r in rows]).correlation,2) for k in ["rho_endo","rho_exo","rho_tot"]}
print("Spearman(PE, .):",sp)
json.dump({"rows":rows,"spearman_PE_vs":sp,"order":4,"delay":1},open("out/permutation_entropy.json","w"),indent=2)
