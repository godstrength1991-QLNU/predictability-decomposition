"""Figure: CRPS gain versus mutual information for four noise families (true conditional laws)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
R=json.load(open("out/nongauss.json"))
sty={"gaussian":("Gaussian","#2166ac","o"),"student_t3":("Student-t (3 d.o.f.)","#b2182b","s"),
     "skewed_exp":("Skewed (exponential)","#1b7837","^"),"heteroscedastic":("Heteroscedastic","#762a83","D")}
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.48,3.8))
for fam,(lab,c,m) in sty.items():
    e=R[fam]["endo_sweep"]; x=R[fam]["exo_sweep"]
    a1.plot([p["I_H"] for p in e],[p["gain_endo"] for p in e],marker=m,color=c,lw=1.2,ms=4.5,label=lab)
    a2.plot([p["I_F_given_H"] for p in x],[p["rel_exo"] for p in x],marker=m,color=c,lw=1.2,ms=4.5)
for ax,xm in [(a1,0.75),(a2,1.15)]:
    xx=np.linspace(0,xm,100); ax.plot(xx,1-np.exp(-xx),"--",color="0.4",lw=1,label=r"Gaussian closed form $1-\exp(-I)$" if ax is a1 else None)
    ax.grid(alpha=0.25); ax.tick_params(labelsize=8)
a1.set_xlabel(r"mutual information $I(Y;X_H)$ [nats]",fontsize=8.5); a1.set_ylabel("relative CRPS gain",fontsize=8.5)
a2.set_xlabel(r"conditional MI $I(Y;X_F\mid X_H)$ [nats]",fontsize=8.5)
a1.text(0.03,0.95,"(a) endogenous",transform=a1.transAxes,fontsize=9,fontweight="bold",va="top")
a2.text(0.03,0.95,"(b) exogenous",transform=a2.transAxes,fontsize=9,fontweight="bold",va="top")
h,l=a1.get_legend_handles_labels()
fig.legend(h,l,loc="lower center",ncol=3,fontsize=6.6,frameon=False,bbox_to_anchor=(0.5,0.0))
plt.tight_layout(rect=[0,0.15,1,1]); plt.savefig("out/_fig_nongauss.pdf")
