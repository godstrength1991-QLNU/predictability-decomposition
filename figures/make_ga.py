import json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
B={r["domain"]:r for r in json.load(open("out/rho_B.json"))}
lab={"DKASC_site13":"solar (desert)","DKASC_site31":"solar","DKASC_M9":"solar",
     "Reservoir(ASOS-net)":"reservoir","HKUST(subtropical PV)":"solar (HK)",
     "Kelmarsh(wind)":"wind","CAMELS(streamflow)":"streamflow"}
col={"DKASC_site13":"#c0392b","DKASC_site31":"#e67e22","DKASC_M9":"#8e44ad",
     "Reservoir(ASOS-net)":"#1a5276","HKUST(subtropical PV)":"#148f4b",
     "Kelmarsh(wind)":"#117a8b","CAMELS(streamflow)":"#2874a6"}
fig,ax=plt.subplots(figsize=(10.6,4.25))
ax.plot([0,0.95],[0,0.95],ls=":",color="0.7",lw=1)
for d,p in B.items():
    mk="D" if d=="Reservoir(ASOS-net)" else "s"
    ax.scatter(p["rho_endo_c"],p["rho_exo_c"],marker=mk,s=140,color=col[d],edgecolor="k",lw=0.7,zorder=5)
ax.annotate("wind / desert solar\nforecast is decisive (NWP)",(0.05,0.80),fontsize=10,color="#c0392b",fontweight="bold",va="center")
ax.annotate("reservoir\nhistory suffices (DL);\nNWP redundant",(0.92,0.06),fontsize=10,color="#1a5276",fontweight="bold",ha="right")
ax.annotate("streamflow / rooftop solar\n(both matter)",(0.44,0.34),fontsize=9,color="0.35")
ax.set_xlim(-0.03,1.0); ax.set_ylim(-0.05,0.92)
ax.set_xlabel(r"endogenous $\rho_{\mathrm{endo}}$  (value of history $\to$ deep learning)",fontsize=11)
ax.set_ylabel(r"exogenous $\rho_{\mathrm{exo}}$  ($\to$ NWP)",fontsize=10.5)
ax.set_title("A predictability map for environmental forecasting\n"
             "one climatology-normalised CRPS decomposition places water, solar \u0026 wind on an inertia\u2194forcing spectrum",
             fontsize=10.5,fontweight="bold")
ax.grid(alpha=0.2)
plt.tight_layout(); 
plt.savefig("out/submission/GraphicalAbstract.png",dpi=130)
plt.savefig("out/submission/GraphicalAbstract.pdf")
from PIL import Image
print("GA size px:", Image.open("out/submission/GraphicalAbstract.png").size)
