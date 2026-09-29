"""Synthetic validation (Proposition 3): linear-Gaussian Y = a*X_H + b*X_F + eps.
For Gaussian conditionals, the log-score gain equals the mutual information
I = log(sigma_before/sigma_after), and the optimal CRPS is sigma/sqrt(pi).
The relative CRPS gain (C_before - C_after)/C_before = 1 - exp(-I) is a strictly
monotone (not linear) function of I, equal to I to first order. CRPS values are
estimated by Monte Carlo (N = 2e5) using the closed-form Gaussian CRPS."""
import numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42; matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
from scipy.stats import norm, spearmanr
rng=np.random.default_rng(42); N=200_000
def mc_crps(sigma):
    y=sigma*rng.standard_normal(N); z=y/sigma      # outcome from the true conditional
    return np.mean(sigma*(z*(2*norm.cdf(z)-1)+2*norm.pdf(z)-1/np.sqrt(np.pi)))
def sweep(I_grid, sig_before, sig_after):
    rel=[]
    for I in I_grid:
        sb,sa=sig_before(I),sig_after(I)
        cb,ca=mc_crps(sb),mc_crps(sa); rel.append((cb-ca)/cb)
    return np.array(rel)
b0=0.5; a0=0.5
I_endo=np.linspace(0.01,0.85,8)   # endogenous: add X_H (b fixed)
I_exo =np.linspace(0.02,1.15,8)   # exogenous: add X_F given X_H (a fixed)
# endo: sigma_before = sqrt(a^2+b^2+1), sigma_after = sqrt(b^2+1); choose a s.t. I target
endo=sweep(I_endo, lambda I: np.sqrt(b0**2+1)*np.exp(I), lambda I: np.sqrt(b0**2+1))
# exo : sigma_before = sqrt(b^2+1) (given X_H), sigma_after = 1
exo =sweep(I_exo,  lambda I: np.exp(I), lambda I: 1.0)
fig,axs=plt.subplots(1,2,figsize=(7.48,3.2))
for ax,I,g,lab,xl in [(axs[0],I_endo,endo,"(a) Endogenous",r"True mutual information $I(Y;X_H)$ [nats]"),
                      (axs[1],I_exo,exo,"(b) Exogenous",r"True conditional MI $I(Y;X_F\mid X_H)$ [nats]")]:
    xx=np.linspace(0,I.max()*1.02,200)
    ax.plot(xx,xx,"--",color="#b2182b",lw=1.2,label=r"Log score: $\Delta=I$ (exact)")
    ax.plot(xx,1-np.exp(-xx),"-",color="0.6",lw=0.9,label=r"Closed form $1-e^{-I}$")
    ax.scatter(I,g,s=28,color="#2166ac",zorder=5,label="Relative CRPS gain (MC)")
    rho=spearmanr(I,g).correlation
    ax.text(0.97,0.05,f"Spearman $\\rho$ = {rho:.2f}",transform=ax.transAxes,ha="right",fontsize=8)
    ax.text(0.03,0.93,lab,transform=ax.transAxes,fontsize=9,fontweight="bold",va="top")
    ax.set_xlabel(xl,fontsize=8.5); ax.set_ylabel("Predictability gain",fontsize=8.5)
    ax.tick_params(labelsize=8); ax.grid(alpha=0.25); ax.legend(fontsize=7,loc="upper left",bbox_to_anchor=(0.0,0.9),frameon=True)
plt.tight_layout()
plt.savefig("out/_fig1_synthetic.pdf")
print("spearman endo/exo:", spearmanr(I_endo,endo).correlation, spearmanr(I_exo,exo).correlation)
print("max |MC - closed form|:", np.max(np.abs(endo-(1-np.exp(-I_endo)))), np.max(np.abs(exo-(1-np.exp(-I_exo)))))
