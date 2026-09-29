"""Fig 1 (theory, synthetic validation): high-resolution re-render of the original
dual-track figure from its exact data (synth_results.npz; Monte Carlo, N = 2e5).
Endogenous: me = true I(Y;X_H), ce = CRPS gap; exogenous: mx = true I(Y;X_F|X_H), cx = CRPS gap."""
import numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
d=np.load("results/synth_results.npz")
me,ce,mx,cx=d["me"],d["ce"],d["mx"],d["cx"]
fig,axes=plt.subplots(1,2,figsize=(7.48,3.1))
for ax,m,c,xl,yl,tl in [(axes[0],me,ce,r'True mutual information $I(Y;X_H)$ [nats]',r'Predictability gain $\Delta_{endo}$','(a) Endogenous'),
                        (axes[1],mx,cx,r'True conditional MI $I(Y;X_F|X_H)$ [nats]',r'Predictability gain $\Delta_{exo}$','(b) Exogenous')]:
    ax.scatter(m,c,c='#2166ac',s=30,zorder=3,label='CRPS gap (MC)')
    ax.plot([0,m.max()],[0,m.max()],'--',c='#b2182b',lw=1.2,label=r'Log score: $\Delta=I$ (exact)')
    ax.set_xlabel(xl,fontsize=8.5); ax.set_ylabel(yl,fontsize=8.5); ax.set_title(tl,fontsize=9.5)
    ax.tick_params(labelsize=8); ax.legend(fontsize=7.5,loc='upper left'); ax.grid(alpha=0.3)
plt.tight_layout()
import os; os.makedirs("out/figures_final",exist_ok=True)
base="out/figures_final/Fig1_synthetic_validation"
plt.savefig(base+".pdf"); plt.savefig(base+".tiff",dpi=1010,pil_kwargs={"compression":"tiff_lzw"}); plt.savefig(base+".png",dpi=600)
print("Spearman endo/exo:",spearmanr(me,ce).correlation,spearmanr(mx,cx).correlation)
