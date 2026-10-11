"""Second estimator family: linear quantile regression (parametric) instead of gradient-boosted
trees. Same samples, information sets, split and quantile levels; features are median-imputed
and standardised on the training data; training rows are subsampled to at most 8000 for speed."""
import json, sys, time, warnings, numpy as np
from sklearn.linear_model import QuantileRegressor
import model_core as M
from run_refit import load, prep
warnings.filterwarnings("ignore")
Q=M.QLEVELS
def crps_lin(long,cols,tr,te,rng):
    X=long[cols].astype(float).values; y=long["target"].astype(float).values
    itr=np.where(tr&~np.isnan(y))[0]; ite=np.where(te&~np.isnan(y))[0]
    if len(itr)>8000: itr=rng.choice(itr,8000,replace=False)
    med=np.nanmedian(X[itr],0); med=np.where(np.isnan(med),0,med); X=np.where(np.isnan(X),med,X)
    mu,sd=X[itr].mean(0),X[itr].std(0); sd[sd==0]=1; Z=(X-mu)/sd
    P=np.column_stack([QuantileRegressor(quantile=q,alpha=0.0,solver="highs").fit(Z[itr],y[itr]).predict(Z[ite]) for q in Q])
    P=np.sort(P,1); u=y[ite][:,None]-P
    return (2/len(Q))*np.mean(np.sum(u*(Q[None,:]-(u<0)),1))
dom=sys.argv[1]; rng=np.random.default_rng(0)
frames,exo,stride=load(dom); long,feats,tr,te=prep(frames,exo,stride)
t=time.time(); C={c:crps_lin(long,feats[c],tr,te,rng) for c in ["clim","hist","full"]}
r=dict(domain=dom,estimator="linear quantile regression",rho_endo=(C["clim"]-C["hist"])/C["clim"],rho_exo=(C["hist"]-C["full"])/C["clim"],crps=C)
json.dump(r,open(f"out/linqr_{dom}.json","w"),indent=2)
print(f"{dom}: linear QR  endo={r['rho_endo']:.3f}  exo={r['rho_exo']:.3f}   ({time.time()-t:.0f}s)")
