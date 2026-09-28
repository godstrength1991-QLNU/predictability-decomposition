import json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
s=json.load(open("out/camels_sweep.json")); s=sorted(s,key=lambda x:x["H"])
H=[r["H"] for r in s]; en=[r["rho_endo_c"] for r in s]; ex=[r["rho_exo_c"] for r in s]; ps=[r["persist_share"] for r in s]
fig,ax=plt.subplots(figsize=(6.6,4.4))
ax.plot(H,en,"o-",color="#c0392b",lw=2,ms=7,label=r"$\rho_{\mathrm{endo}}$ (history)")
ax.plot(H,ex,"s-",color="#1a5276",lw=2,ms=7,label=r"$\rho_{\mathrm{exo}}$ (future forcing)")
ax.plot(H,ps,"^--",color="0.5",lw=1.6,ms=6,label="persistence share")
for x,y in zip(H,en): ax.annotate(f"{y:.2f}",(x,y),textcoords="offset points",xytext=(0,8),fontsize=8,color="#c0392b",ha="center")
for x,y in zip(H,ex): ax.annotate(f"{y:.2f}",(x,y),textcoords="offset points",xytext=(0,-13),fontsize=8,color="#1a5276",ha="center")
ax.set_xscale("log"); ax.set_xticks(H); ax.set_xticklabels([str(h) for h in H])
ax.set_xlabel("forecast horizon $H$ (days, log scale)",fontsize=11)
ax.set_ylabel("climatology-normalised coefficient",fontsize=11)
ax.set_ylim(0,0.58); ax.grid(alpha=0.25)
ax.set_title("CAMELS streamflow: decomposition vs. forecast horizon\n"
             "memory advantage ($\\rho_{\\mathrm{endo}}$) decays with lead time; forcing value stays flat",fontsize=10)
ax.legend(fontsize=9,frameon=True,loc="upper right")
plt.tight_layout()
import os as _os; _os.makedirs("out/submission",exist_ok=True)
for _p,_d in [("out/Fig4_horizon_sweep.png",200),("out/submission/Fig4_horizon_sweep.png",600)]: plt.savefig(_p,dpi=_d)
plt.savefig("out/submission/Fig4_horizon_sweep.pdf"); plt.close()
print("saved out/Fig4_horizon_sweep.png")
