"""Figure: finite-sample bias of the coefficient estimator (synthetic data with known truth)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'font.family':'sans-serif'})
import matplotlib.pyplot as plt
R=json.load(open("out/consistency.json")); T=R["true"]
ns=sorted(int(n) for n in R["runs"])
fig,ax=plt.subplots(figsize=(3.31,2.6))
for key,lab,c,m in [("rho_endo",r"$\hat\rho_{\mathrm{endo}}-\rho_{\mathrm{endo}}$","#b2182b","o"),("rho_exo",r"$\hat\rho_{\mathrm{exo}}-\rho_{\mathrm{exo}}$","#2166ac","s")]:
    v=[np.array([r[key] for r in R["runs"][str(n)]])-T[key] for n in ns]
    mu=[x.mean() for x in v]; sd=[x.std(ddof=1) for x in v]
    ax.errorbar(ns,mu,yerr=sd,fmt=m+"-",color=c,lw=1.3,ms=4,capsize=2,label=lab)
ax.axhline(0,color="0.5",lw=0.8); ax.set_xscale("log")
ax.set_xlabel("training sample size",fontsize=8); ax.set_ylabel("estimation error (mean ± s.d.)",fontsize=8)
ax.tick_params(labelsize=8); ax.grid(alpha=0.25); ax.legend(fontsize=7.5,loc="lower right",frameon=True)
plt.tight_layout(); plt.savefig("out/_fig_consistency.pdf")
