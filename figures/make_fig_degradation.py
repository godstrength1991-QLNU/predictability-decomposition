"""Fig 7: value of an imperfect forecast (rho_exo) versus forecast-error level."""
import json, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
doms=[("kelmarsh","Kelmarsh wind","#117a8b","s"),("DKASC_site13","DKASC Site 13","#c0392b","s"),
      ("hkust","HKUST PV (cap.-norm.)","#148f4b","s"),("DKASC_M9","DKASC M9","#8e44ad","s"),
      ("DKASC_site31","DKASC Site 31","#e67e22","s"),("camels","CAMELS streamflow","#2874a6","o")]
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.48,3.2))
for key,lab,c,m in doms:
    d=json.load(open(f"out/degrade_{key}.json")); lam=[r["lam"] for r in d["curve"]]
    a1.plot(lam,[r["rho_exo"] for r in d["curve"]],marker=m,color=c,lw=1.5,ms=5,label=lab)
    a2.plot(lam,[r["retained"]*100 for r in d["curve"]],marker=m,color=c,lw=1.5,ms=5)
for ax in (a1,a2):
    ax.set_xticks([0,0.25,0.5,1.0]); ax.grid(alpha=0.25); ax.tick_params(labelsize=8)
    ax.set_xlabel(r"forecast error $\lambda$ (noise s.d. / variable s.d.)",fontsize=8.5)
a1.set_ylabel(r"$\rho_{\mathrm{exo}}(\lambda)$",fontsize=9); a1.set_ylim(0,0.9)
a2.set_ylabel(r"retained forecast value (%)",fontsize=9); a2.set_ylim(0,115)
a1.text(0.97,0.97,"(a)",transform=a1.transAxes,ha="right",va="top",fontsize=9.5,fontweight="bold")
a2.text(0.97,0.97,"(b)",transform=a2.transAxes,ha="right",va="top",fontsize=9.5,fontweight="bold")
h,l=a1.get_legend_handles_labels(); a2.legend(h,l,fontsize=6.8,loc="lower left",frameon=True)
plt.tight_layout(); plt.savefig("out/_fig7.pdf")
