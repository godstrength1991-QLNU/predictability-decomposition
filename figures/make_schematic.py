import matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42; import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig,ax=plt.subplots(figsize=(9.0,4.6)); ax.axis("off")
# illustrative CRPS levels (schematic)
lv={"clim":1.00,"persist":0.72,"hist":0.55,"full":0.22,"climfut":0.66}
xpos={"clim":0.06,"persist":0.30,"hist":0.54,"full":0.78}
inp={"clim":"calendar only","persist":"+ current value $y_t$",
     "hist":"+ history\n+ past forcing","full":"+ future\nforcing $x_{t+k}$"}
col="#34495e"
for k in ["clim","persist","hist","full"]:
    h=lv[k]*0.62; x=xpos[k]
    ax.add_patch(FancyBboxPatch((x,0.32),0.15,h,boxstyle="round,pad=0.006",
        fc="#eaf2f8",ec=col,lw=1.3))
    ax.text(x+0.075,0.32+h+0.03,f"$\\mathsf{{{k}}}$",ha="center",fontsize=11,fontweight="bold",color=col)
    ax.text(x+0.075,0.20,inp[k],ha="center",va="top",fontsize=8.5,color="0.25")
    ax.text(x+0.075,0.34,f"CRPS",ha="center",fontsize=7,color="0.5")
# climfut box (branch)
x=xpos["full"]; h=lv["climfut"]*0.62
ax.add_patch(FancyBboxPatch((x+0.20,0.32),0.15,h,boxstyle="round,pad=0.006",fc="#fdecea",ec="#c0392b",lw=1.2,ls="--"))
ax.text(x+0.275,0.32+h+0.03,r"$\mathsf{climfut}$",ha="center",fontsize=10.5,fontweight="bold",color="#c0392b")
ax.text(x+0.275,0.20,"calendar\n+ future forcing\n(no history)",ha="center",va="top",fontsize=8,color="#c0392b")
# gap arrows (rho definitions) along the top
def gap(x1,x2,y,label,c):
    ax.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle="<->",mutation_scale=11,color=c,lw=1.4))
    ax.text((x1+x2)/2,y+0.025,label,ha="center",fontsize=9.5,color=c,fontweight="bold")
gap(xpos["clim"]+0.075, xpos["hist"]+0.075, 1.04, r"$\rho_{\mathrm{endo}}=(\mathrm{CRPS}_{\mathsf{clim}}-\mathrm{CRPS}_{\mathsf{hist}})/\mathrm{CRPS}_{\mathsf{clim}}$", "#1a5276")
gap(xpos["hist"]+0.075, xpos["full"]+0.075, 0.93, r"$\rho_{\mathrm{exo}}=(\mathrm{CRPS}_{\mathsf{hist}}-\mathrm{CRPS}_{\mathsf{full}})/\mathrm{CRPS}_{\mathsf{clim}}$", "#148f4b")
ax.text(0.5,0.055,r"redundancy $R=(\mathrm{CRPS}_{\mathsf{clim}}-\mathrm{CRPS}_{\mathsf{climfut}})/\mathrm{CRPS}_{\mathsf{clim}}-\rho_{\mathrm{exo}}$   ($R>0$ redundant, $R<0$ synergistic)",
        ha="center",fontsize=9,color="#c0392b")
ax.set_xlim(0,1.20); ax.set_ylim(0,1.10)
plt.tight_layout()
import os; os.makedirs("out/submission",exist_ok=True)
plt.savefig("out/Fig_framework.png",dpi=200); plt.savefig("out/submission/Fig_framework.pdf"); plt.savefig("out/submission/Fig_framework.png",dpi=600)
print("saved Fig_framework")
