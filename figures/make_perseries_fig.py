import json, numpy as np, matplotlib; matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42; import matplotlib.pyplot as plt
np.random.seed(0)
hk=json.load(open("out/perseries_hkust.json")); cm=json.load(open("out/perseries_camels.json"))
def arr(o,k): return np.array([x[k] for x in o if x[k] is not None])
fig,(a1,a2)=plt.subplots(1,2,figsize=(9.4,4.3))
for ax,o,cols,ttl in [(a1,hk,["#8e44ad","#148f4b"],None),(a2,cm,["#2874a6","#e67e22"],None)]:
    b=ax.boxplot([arr(o,"endo"),arr(o,"exo")],labels=[r"$\rho_{\mathrm{endo}}$",r"$\rho_{\mathrm{exo}}$"],
                 patch_artist=True,widths=0.5,showfliers=False,medianprops=dict(color="k"))
    for p,c in zip(b["boxes"],cols): p.set_facecolor(c); p.set_alpha(0.5)
    for i,k in enumerate(["endo","exo"],1):
        y=arr(o,k); ax.scatter(np.random.normal(i,0.05,len(y)),y,s=11,color="0.3",alpha=0.5,zorder=3)
    ax.axhline(0,color="0.8",lw=0.8); ax.grid(alpha=0.2,axis="y")
rf=arr(hk,"redu_frac")*100
a1.set_ylabel("climatology-normalised coefficient")
a1.set_ylim(top=max(arr(hk,"endo").max(),arr(hk,"exo").max())*1.18)
a2.set_ylim(top=max(arr(cm,"endo").max(),arr(cm,"exo").max())*1.15)
a1.text(0.03,0.97,f"(a) HKUST, per site (n={len(hk)})",transform=a1.transAxes,fontsize=9.5,fontweight="bold",va="top")
a2.text(0.97,0.97,f"(b) CAMELS, per basin (n={len(cm)})",transform=a2.transAxes,fontsize=9.5,fontweight="bold",va="top",ha="right")
plt.tight_layout()
import os; os.makedirs("out/submission",exist_ok=True)
for p,d in [("out/Fig_distributions.png",200),("out/submission/Fig_distributions.png",600)]: plt.savefig(p,dpi=d)
plt.savefig("out/submission/Fig_distributions.pdf"); print("saved Fig_distributions")
