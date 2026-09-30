import json, pickle, numpy as np, subprocess, re
from scipy.stats import spearmanr
J=lambda f: json.load(open(f"out/{f}.json"))
T=subprocess.run(["pdftotext","merge/B8_full_manuscript.pdf","-"],capture_output=True,text=True).stdout
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
syn=np.load("oldfig/b8_oldfig_pack/synth_results.npz"); claim("synthetic Spearman","Spearman ρ = 1.00",spearmanr(syn["me"],syn["ce"]).correlation==1.0 and spearmanr(syn["mx"],syn["cx"]).correlation==1.0)
k=np.load("oldfig/b8_oldfig_pack/ksg_results.npz"); claim("KSG sine Spearman","falls to 0.89",round(spearmanr(k["me"],k["ce"]).correlation,2)==0.89)
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
