import json, pickle, numpy as np, subprocess, re
from scipy.stats import spearmanr
J=lambda f: json.load(open(f"out/{f}.json"))
T=subprocess.run(["pdftotext","serra/Manuscript.pdf","-"],capture_output=True,text=True).stdout
T=re.sub(r"\s+"," ",T).replace("−","-").replace("–","-")
B={r["domain"]:r for r in J("rho_B")}; issues=[]; ok=0
def claim(desc,text_fragment,cond):
    global ok
    present=text_fragment in T
    if not present: issues.append(f"[text not found] {desc}: '{text_fragment}'")
    elif not cond: issues.append(f"[value mismatch] {desc}: '{text_fragment}'")
    else: ok+=1
r=B["Reservoir(ASOS-net)"]; claim("reservoir exo estimate","the estimate, -0.004,",round(r["rho_exo_c"],3)==-0.004)
sw=sorted(J("camels_sweep"),key=lambda x:x["H"])
claim("sweep endo H=1","from ρendo = 0.52 at H = 1",round(sw[0]["rho_endo_c"],2)==0.52)
claim("sweep endo H=30","to 0.22 at H = 30",round(sw[-1]["rho_endo_c"],2)==0.22)
ex=[x["rho_exo_c"] for x in sw]; claim("sweep exo range","between 0.10 and 0.14",round(min(ex),2)==0.10 and round(max(ex),2)==0.14)
cm=pickle.load(open("data/camels/camels_cache.pkl","rb"))["frames"]
n_sweep=len(cm[::5]); claim("horizon-sweep subset size",f"{n_sweep}-basin subset",True)
claim("CAMELS main pool size","CAMELS streamflow (46)",len(cm[::2])==46)
m9=[b["rho_exo"] for b in J("rolling_M9")["blocks"]]; claim("rolling M9 exo range","0.35-0.58 for M9",round(min(m9),2)==0.35 and round(max(m9),2)==0.58)
hk=J("perseries_hkust"); rf=np.array([x["redu_frac"] for x in hk if x["redu_frac"] is not None])
claim("per-site HKUST median redundancy","median +1%",round(np.median(rf)*100)==1)
claim("per-site HKUST share R>0","58% of sites",round((rf>0).mean()*100)==58)
claim("per-series HKUST n","34 HKUST sites",len(hk)==34); claim("per-series CAMELS n","30 CAMELS basins",len(J("perseries_camels"))==30)
sh=J("shapley_attribution"); claim("Shapley max","most 0.09",round(sh["max_abs_half_R"],2)==0.09)
syn=np.load("out/synth_results.npz"); claim("synthetic Spearman","Spearman ρ = 1.00",spearmanr(syn["me"],syn["ce"]).correlation==1.0 and spearmanr(syn["mx"],syn["cx"]).correlation==1.0)
k=np.load("out/ksg_results.npz"); claim("KSG sine Spearman","falls to 0.89",round(spearmanr(k["me"],k["ce"]).correlation,2)==0.89)
claim("KSG MI saturation range","(0.17-0.19 nats)",round(sorted(k["me"])[2],2)==0.17 and round(k["me"].max(),2)==0.19)
log=open("out/ksg_v3_rerun_log.txt").read(); claim("KSG tanh/cubic","(Spearman ρ = 1.00)",log.count("1.0000")>=2)
st=pickle.load(open("data/dkasc_cache.pkl","rb"))
def ratio(s):
    d=st[s]["daily"]; return (d["y"].groupby(d.index.year).mean()/d["Global_Horizontal_Radiation"].groupby(d.index.year).mean())
r31=ratio("DKASC_site31"); claim("Site31 decline 2014-2024","declines by about 32%",round((1-r31[2024]/r31[2014])*100)==32)
r9=ratio("DKASC_M9"); low=r9[[2019,2020,2021]].mean()/r9[[2013,2014,2015,2016]].mean()
claim("M9 drop to ~40%","about 40% of its initial level",abs(low-0.40)<0.03)
for dk in ["kelmarsh","DKASC_site13","DKASC_site31","DKASC_M9","hkust","camels"]:
    d=J(f"degrade_{dk}"); dom=d["domain"]; b=B.get(dom) or B.get("HKUST(subtropical PV)")
    if abs(d["curve"][0]["rho_exo"]-b["rho_exo_c"])>1e-9: issues.append(f"[fig6 lambda=0 != Table 2] {dk}: {d['curve'][0]['rho_exo']:.4f} vs {b['rho_exo_c']:.4f}")
    else: ok+=1
print(f"TEXT/FIGURE CHECKS OK: {ok}   ISSUES: {len(issues)}"); [print("  ",i) for i in issues]

# ===== checks for the SERRA additions =====
import json
T2=T.replace("–","-")
iss2=[]; ok2=0
def chk2(desc,frag,cond):
    global ok2
    if frag not in T2: iss2.append(f"[text not found] {desc}: '{frag}'")
    elif not cond: iss2.append(f"[value mismatch] {desc}: '{frag}'")
    else: ok2+=1
C=json.load(open("out/consistency.json")); tr=C["true"]
b=lambda n,k: np.mean([r[k] for r in C["runs"][str(n)]])-tr[k]
chk2("consistency endo n=200","from -0.042 to -0.006 for",round(b(200,"rho_endo"),3)==-0.042 and round(b(20000,"rho_endo"),3)==-0.006)
chk2("consistency exo","from -0.080 to -0.002 for",round(b(200,"rho_exo"),3)==-0.080 and round(b(20000,"rho_exo"),3)==-0.002)
chk2("true coefficients in caption","0.158",round(tr["rho_endo"],3)==0.158 and round(tr["rho_exo"],3)==0.303)
NG=json.load(open("out/nongauss.json"))
dev=lambda f: np.mean([abs(p["rel_exo"]-(1-np.exp(-p["I_F_given_H"]))) for p in NG[f]["exo_sweep"]])
chk2("non-Gaussian deviations","by 0.09 and 0.07",round(dev("skewed_exp"),2)==0.09 and round(dev("heteroscedastic"),2)==0.07)
chk2("non-Gaussian Spearman","Spearman correlation 1.00 in both directions",all(round(v["spearman_endo"],2)==1 and round(v["spearman_exo"],2)==1 for v in NG.values()))
RF={r["domain"]:r for r in json.load(open("out/refit_summary.json"))}
chk2("CAMELS refit sd","(standard deviations of 0.001 for CAMELS)",round(RF["CAMELS(streamflow)"]["endo_refit_sd"],3)==0.001 and round(RF["CAMELS(streamflow)"]["exo_refit_sd"],3)==0.001)
ratios=[RF[k]["endo_refit_sd"]/RF[k]["endo_boot_sd"] for k in ["DKASC_site13","DKASC_site31","DKASC_M9"]]
chk2("DKASC refit/boot ratio","three to five times",3<=min(ratios) and max(ratios)<5.5)
rr=RF["Reservoir(ASOS-net)"]; chk2("reservoir exo refit ratio","about five times larger",4<=rr["exo_refit_sd"]/rr["exo_boot_sd"]<=5.5)
R=json.load(open("out/refit_reservoir.json"))["runs"]; xs=[r["rho_exo"] for r in R]
chk2("reservoir exo refit range","ranges from -0.004 to 0.016",round(min(xs),3)==-0.004 and round(max(xs),3)==0.016)
chk2("35 refits","None of the 35",sum(len(json.load(open(f"out/refit_{k}.json"))["runs"]) for k in ["reservoir","camels","hkust","DKASC_M9","DKASC_site31","DKASC_site13","kelmarsh"])==35)
LQ=json.load(open("out/linqr_summary.json")); h=[r for r in LQ["rows"] if r["domain"]=="HKUST(subtropical PV)"][0]
chk2("linear QR Spearman exo","(Spearman correlation 1.00)",round(LQ["summary"]["spearman_exo"],2)==1.0)
chk2("HKUST linear QR endo",f"={h['lin_endo']:.3f}$" if False else f"{h['lin_endo']:.3f}",True)
chk2("all regimes agree (7/7)","All seven domains fall in the same",all(r["regime_agrees"] for r in LQ["rows"]))
N=json.load(open("out/nwp_summary.json"))["retained_by_lead"]
p=lambda k,m: f"{N[str(k)][m]*100:.0f}"
chk2("NWP GFS bc leads 1,2,5",f"GFS retains {p(1,'gfs_bc')}% and {p(2,'gfs_bc')}% at lead times of one and two days and {p(5,'gfs_bc')}% at five days",True)
chk2("NWP ECMWF bc",f"ECMWF {p(1,'ecmwf_bc')}%, {p(2,'ecmwf_bc')}% and {p(5,'ecmwf_bc')}%",True)
vals=[N[str(k)][m] for k in range(1,6) for m in ("gfs_bc","ecmwf_bc")]
chk2("abstract range 20-41%","retain 20-41% of the perfect-forecast value",round(min(vals)*100)==20 and round(max(vals)*100)==41)
n=sum(json.load(open(f"out/nwp_{s}.json"))["n_test"] for s in ["DKASC_site13","DKASC_site31"])
chk2("NWP test size",f"({n} forecasts",True)
chk2("observed share 26-41% at 1-2 days","against 26-41% observed",round(min(N[k][m] for k in "12" for m in ("gfs_bc","ecmwf_bc"))*100)==26 and round(max(N[k][m] for k in "12" for m in ("gfs_bc","ecmwf_bc"))*100)==41)
print(f"SERRA ADDITIONS OK: {ok2}   ISSUES: {len(iss2)}"); [print("  ",i) for i in iss2]
