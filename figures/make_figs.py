import json, numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42; import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
B={r["domain"]:r for r in json.load(open("out/rho_B.json"))}
A={r["domain"]:r for r in json.load(open("out/rho_A.json"))}
EN,EX="rho_endo_c","rho_exo_c"
order=["Kelmarsh(wind)","DKASC_site13","DKASC_site31","CAMELS(streamflow)","HKUST(subtropical PV)","DKASC_M9","Reservoir(ASOS-net)"]
lab={"DKASC_site13":"DKASC Site 13","DKASC_site31":"DKASC Site 31","DKASC_M9":"DKASC M9",
     "Reservoir(ASOS-net)":"Reservoir (403 dams)","HKUST(subtropical PV)":"HKUST PV (58 sites)",
     "Kelmarsh(wind)":"Kelmarsh wind (6 turb.)","CAMELS(streamflow)":"CAMELS streamflow (46)"}
col={"DKASC_site13":"#c0392b","DKASC_site31":"#e67e22","DKASC_M9":"#8e44ad",
     "Reservoir(ASOS-net)":"#1a5276","HKUST(subtropical PV)":"#148f4b",
     "Kelmarsh(wind)":"#117a8b","CAMELS(streamflow)":"#2874a6"}
def err(p,key):  # asymmetric err from CI
    lo,hi=p["ci_"+key]; v=p[{"endo":EN,"exo":EX}[key]]
    return [[max(0,v-lo)],[max(0,hi-v)]]

# ---------- FIG 1: quadrant with bootstrap error bars ----------
fig,ax=plt.subplots(figsize=(8,6.9))
XMAX,YMIN,YMAX=1.0,-0.12,0.92
ax.axhline(0,color="0.8",lw=0.8); ax.axhline(0.30,color="0.92",lw=1); ax.axvline(0.30,color="0.92",lw=1)
ax.plot([0,YMAX],[0,YMAX],ls=":",color="0.65",lw=1)
ax.text(0.30,0.90,"FORCING-DOMINATED\nfuture weather is key",fontsize=9,color="#c0392b",fontweight="bold",va="top")
ax.text(0.97,0.90,"DUAL\nboth matter",fontsize=9,color="0.5",ha="right",va="top")
ax.text(0.97,0.17,"INERTIA-DOMINATED\nhistory suffices \u00b7 NWP useless",fontsize=9,color="#1a5276",fontweight="bold",ha="right",va="bottom")
ax.text(0.02,-0.02,"low predictability",fontsize=8,color="0.55",va="top")
dk=["DKASC_site13","DKASC_site31","DKASC_M9"]
for s in dk:  # A->B arrows
    ax_,ay_=A[s][EN],A[s][EX]; bx_,by_=B[s][EN],B[s][EX]
    ax.add_patch(FancyArrowPatch((ax_,ay_),(bx_,by_),arrowstyle="-|>",mutation_scale=11,color=col[s],lw=1.2,alpha=0.55,zorder=2))
    ax.scatter([ax_],[ay_],marker="o",s=70,color=col[s],edgecolor="k",lw=0.5,alpha=0.8,zorder=3)
for d in order:
    p=B[d]; c=col[d]; mk="D" if d=="Reservoir(ASOS-net)" else "s"; sz=200 if mk=="D" else 130
    ax.errorbar(p[EN],p[EX],xerr=err(p,"endo"),yerr=err(p,"exo"),fmt="none",ecolor=c,elinewidth=1.1,capsize=2,alpha=0.9,zorder=4)
    ax.scatter(p[EN],p[EX],marker=mk,s=sz,color=c,edgecolor="k",lw=0.7,zorder=5)
# labels
off={"Reservoir(ASOS-net)":(-14,-2,"right","center"),"Kelmarsh(wind)":(11,0,"left","center"),
     "DKASC_site13":(9,6,"left","bottom"),"HKUST(subtropical PV)":(8,6,"left","bottom"),
     "DKASC_M9":(9,-11,"left","top"),"DKASC_site31":(9,7,"left","bottom"),"CAMELS(streamflow)":(8,-11,"left","top")}
for d in order:
    p=B[d]; dx,dy,ha,va=off[d]
    t=lab[d]+(f"\npersist_share={p['persist_share']:.2f}" if d=="Reservoir(ASOS-net)" else "")
    ax.annotate(t,(p[EN],p[EX]),textcoords="offset points",xytext=(dx,dy),fontsize=8.5 if d.startswith("DKASC") else 9,
                color=col[d],fontweight="bold",ha=ha,va=va)
import json as _json
_rawhk=_json.load(open("out/enr_hkust.json"))
ax.scatter(_rawhk["rho_endo_c"],_rawhk["rho_exo_c"],marker="s",s=90,facecolor="none",edgecolor=col["HKUST(subtropical PV)"],lw=1.1,alpha=0.7,zorder=4)
ax.annotate("",(B["HKUST(subtropical PV)"]["rho_endo_c"],B["HKUST(subtropical PV)"]["rho_exo_c"]),xytext=(_rawhk["rho_endo_c"],_rawhk["rho_exo_c"]),arrowprops=dict(arrowstyle="->",color=col["HKUST(subtropical PV)"],lw=1.0,ls=":",alpha=0.7),zorder=3)
ax.annotate("raw pooled",(_rawhk["rho_endo_c"],_rawhk["rho_exo_c"]),textcoords="offset points",xytext=(6,-10),fontsize=7.5,color=col["HKUST(subtropical PV)"],alpha=0.8)
leg=[Line2D([0],[0],marker="D",color="w",markerfacecolor="0.3",markeredgecolor="k",ms=11,label="Reservoir (daily, 7 d)"),
     Line2D([0],[0],marker="o",color="w",markerfacecolor="0.3",markeredgecolor="k",ms=8,label="Solar Horizon A (intraday, 24 h)"),
     Line2D([0],[0],marker="s",color="w",markerfacecolor="0.3",markeredgecolor="k",ms=10,label="Daily, 7 d (solar/wind/streamflow)"),
     Line2D([0],[0],color="0.3",lw=1.2,label="A \u2192 B shift"),
     Line2D([0],[0],color="0.3",lw=1.1,marker="|",label="95% bootstrap CI")]
ax.legend(handles=leg,loc="center",fontsize=8,frameon=True,bbox_to_anchor=(0.64,0.585))
ax.set_xlim(-0.05,XMAX); ax.set_ylim(YMIN,YMAX)
ax.set_xlabel(r"$\rho_{\mathrm{endo}}$  (endogenous — value of history, vs climatology)",fontsize=11)
ax.set_ylabel(r"$\rho_{\mathrm{exo}}$  (exogenous — marginal value of a perfect forecast)",fontsize=11)
plt.tight_layout()
import os as _os; _os.makedirs("out/submission",exist_ok=True)
for _p,_d in [("out/Fig1_quadrant.png",200),("out/submission/Fig1_quadrant.png",600)]: plt.savefig(_p,dpi=_d)
plt.savefig("out/submission/Fig1_quadrant.pdf"); plt.close()
print("saved Fig1 (with CIs)")

# ---------- FIG 2: forecast value standalone vs given-history (gap = redundancy) ----------
fig,ax=plt.subplots(figsize=(9,5.4))
xs=np.arange(len(order)); w=0.38
for i,d in enumerate(order):
    p=B[d]
    ax.bar(i-w/2, p["exo_given_clim"], w, color=col[d], alpha=0.45, edgecolor="k", lw=0.5,
           label="forecast value alone (vs climatology)" if i==0 else None)
    ax.bar(i+w/2, p["rho_exo_c"],     w, color=col[d], alpha=0.95, edgecolor="k", lw=0.5,
           label="forecast value given history (marginal)" if i==0 else None)
    rf=p["redundancy_frac"]*100
    tag=f"{rf:.0f}%" if rf>=0 else f"syn {abs(rf):.0f}%"
    top=max(p["exo_given_clim"],p["rho_exo_c"])
    ax.text(i, top+0.03, tag, ha="center", fontsize=8.5, fontweight="bold",
            color=("#1a5276" if rf>60 else "#c0392b" if rf<10 else "0.3"))
ax.axhline(0,color="0.6",lw=0.8)
ax.set_xticks(xs); ax.set_xticklabels([lab[d].split(" (")[0] for d in order], rotation=18, ha="right", fontsize=9)
ax.set_ylabel(r"Value of a perfect forecast  ($\Delta$CRPS / CRPS$_{\mathrm{clim}}$)", fontsize=11)
ax.legend(fontsize=9, frameon=True, loc="upper right")
ax.margins(y=0.15)
plt.tight_layout()
for _p,_d in [("out/Fig2_redundancy.png",200),("out/submission/Fig2_redundancy.png",600)]: plt.savefig(_p,dpi=_d)
plt.savefig("out/submission/Fig2_redundancy.pdf"); plt.close()
print("saved Fig2 (redundancy)")

# ---------- results CSV (enriched) ----------
import csv
rows=[]
for d in ["Reservoir(ASOS-net)","CAMELS(streamflow)","DKASC_site13","DKASC_site31","DKASC_M9","HKUST(subtropical PV)","Kelmarsh(wind)"]:
    p=B[d]; rows.append([lab[d],round(p["persist_share"],3),round(p[EN],3),f"[{p['ci_endo'][0]},{p['ci_endo'][1]}]",
        round(p[EX],3),f"[{p['ci_exo'][0]},{p['ci_exo'][1]}]",round(p["exo_given_clim"],3),
        round(p["redundancy"],3),round(p["redundancy_frac"],3)])
with open("out/rho_results.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["domain","persist_share","rho_endo","ci_endo","rho_exo","ci_exo",
        "exo_given_clim","redundancy","redundancy_frac"]); w.writerows(rows)
print("\n{:22s} {:>6s} {:>6s} {:>7s} {:>8s} {:>6s}".format("domain","p_shr","endo","exo","exo|clim","redu%"))
for d in order:
    p=B[d]; print("{:22s} {:6.2f} {:6.2f} {:7.2f} {:8.2f} {:6.0f}".format(lab[d].split(" (")[0],p["persist_share"],p[EN],p[EX],p["exo_given_clim"],p["redundancy_frac"]*100))
