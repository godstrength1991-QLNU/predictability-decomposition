"""Non-Gaussian synthetic validation of the CRPS-information relation (Proposition 3 beyond
location-scale families). Y = a X_H + b X_F + eps, X_H, X_F ~ N(0,1). CRPS of the TRUE
conditional laws is computed by Monte Carlo (energy form E|Z-y| - E|Z-Z'|/2, Z drawn from the
conditional law); mutual information is estimated with the KSG estimator (k=5)."""
import json, sys, numpy as np
from scipy.spatial import cKDTree
from scipy.special import digamma
from scipy.stats import spearmanr
rng=np.random.default_rng(7)
def noise(fam,size,xf=None):
    if fam=="gaussian": return rng.standard_normal(size)
    if fam=="student_t3": return rng.standard_t(3,size)/np.sqrt(3.0)          # unit variance
    if fam=="skewed_exp": return rng.exponential(1.0,size)-1.0                # mean 0, var 1
    if fam=="heteroscedastic": return rng.standard_normal(size)*np.exp(0.5*xf) # scale depends on X_F
def ksg(x,y,k=5):
    x=(x-x.mean(0))/x.std(0); y=(y-y.mean())/y.std(); n=len(y); xy=np.c_[x,y]
    d=cKDTree(xy).query(xy,k+1,p=np.inf)[0][:,-1]-1e-12
    nx=np.array([len(v)-1 for v in cKDTree(x).query_ball_point(x,d,p=np.inf)])
    ny=np.array([len(v)-1 for v in cKDTree(y[:,None]).query_ball_point(y[:,None],d,p=np.inf)])
    return max(0.0,digamma(k)+digamma(n)-np.mean(digamma(nx+1)+digamma(ny+1)))
def crps_mc(Z,y):          # Z: n x m samples of the predictive law
    t1=np.abs(Z-y[:,None]).mean(1); Zs=np.sort(Z,1); m=Z.shape[1]
    w=(2*np.arange(1,m+1)-m-1)/(m*m); t2=(Zs*w).sum(1)    # E|Z-Z'|/2 via sorted samples
    return np.mean(t1-t2)
def point(fam,a,b,N=1500,M=300,nmi=4000):
    XH,XF=rng.standard_normal((2,N)); y=a*XH+b*XF+noise(fam,N,XF)
    # predictive samples from the true conditional laws
    zf=lambda xh,xf: a*xh[:,None]+b*xf[:,None]+noise(fam,(N,M),np.repeat(xf[:,None],M,1))
    xf_new=rng.standard_normal((N,M))
    ZH=a*XH[:,None]+b*xf_new+noise(fam,(N,M),xf_new)
    x0h,x0f=rng.standard_normal((2,N,M)); Z0=a*x0h+b*x0f+noise(fam,(N,M),x0f)
    S0,SH,SF=crps_mc(Z0,y),crps_mc(ZH,y),crps_mc(zf(XH,XF),y)
    h,f=rng.standard_normal((2,nmi)); yy=a*h+b*f+noise(fam,nmi,f)
    IH=ksg(h[:,None],yy); IHF=ksg(np.c_[h,f],yy)
    return dict(a=a,b=b,I_H=IH,I_F_given_H=max(0.0,IHF-IH),gain_endo=(S0-SH)/S0,gain_exo=(SH-SF)/S0,rel_exo=(SH-SF)/SH)
fams=sys.argv[1].split(","); res={}
for fam in fams:
    endo=[point(fam,a,0.8) for a in np.linspace(0.05,2.0,8)]
    exo=[point(fam,0.8,b) for b in np.linspace(0.05,2.0,8)]
    se=spearmanr([p["I_H"] for p in endo],[p["gain_endo"] for p in endo]).correlation
    sx=spearmanr([p["I_F_given_H"] for p in exo],[p["rel_exo"] for p in exo]).correlation
    res[fam]=dict(endo_sweep=endo,exo_sweep=exo,spearman_endo=se,spearman_exo=sx)
    print(f"{fam:15s} Spearman(I, CRPS gain): endogenous {se:.3f} | exogenous {sx:.3f}")
    print("   endo  I_H:",[round(p["I_H"],2) for p in endo]," gain:",[round(p["gain_endo"],3) for p in endo])
    print("   exo   I_F|H:",[round(p["I_F_given_H"],2) for p in exo]," gain:",[round(p["rel_exo"],3) for p in exo])
import os; fn="out/nongauss.json"; old=json.load(open(fn)) if os.path.exists(fn) else {}; old.update(res); json.dump(old,open(fn,"w"),indent=2)
