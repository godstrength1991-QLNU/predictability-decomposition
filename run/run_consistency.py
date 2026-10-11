"""Finite-sample behaviour of the coefficient estimator on synthetic data with known truth.
Y = a X_H + b X_F + e, X_H, X_F, e ~ N(0,1) independent. True coefficients from Corollary 1:
rho_endo = 1 - s_H/s_0, rho_exo = (s_H - s_HF)/s_0, with s_0=sqrt(a^2+b^2+1), s_H=sqrt(b^2+1), s_HF=1.
The quantile-averaged CRPS of the true Gaussian conditional is proportional to sigma, so these
ratios are also the population targets of the estimator. Same learner and settings as the paper."""
import json, sys, numpy as np, lightgbm as lgb
import model_core as M
a,b=1.0,1.2; s0,sH,sHF=np.sqrt(a*a+b*b+1),np.sqrt(b*b+1),1.0
TRUE={"rho_endo":1-sH/s0,"rho_exo":(sH-sHF)/s0}
Q=M.QLEVELS
def crps(y,P): # P: n x K quantiles; CRPS ~ 2/K sum pinball
    u=y[:,None]-P; return (2/len(Q))*np.mean(np.sum(u*(Q[None,:]-(u<0)),axis=1))
def fit_pred(Xtr,ytr,Xte):
    if Xtr is None: return np.tile(np.quantile(ytr,Q),(len(Xte),1))
    P=[]
    for q in Q:
        m=lgb.LGBMRegressor(objective="quantile",alpha=q,**{**M.LGB,"n_estimators":150,"verbose":-1}); m.fit(Xtr,ytr); P.append(m.predict(Xte))
    return np.sort(np.column_stack(P),axis=1)
rng=np.random.default_rng(int(sys.argv[2]) if len(sys.argv)>2 else 0)
def one(n,nte=20000):
    def draw(m):
        XH,XF,e=rng.standard_normal((3,m)); return XH,XF,a*XH+b*XF+e
    XH,XF,y=draw(n); XHt,XFt,yt=draw(nte)
    C0=crps(yt,fit_pred(None,y,np.zeros(nte)))
    CH=crps(yt,fit_pred(XH[:,None],y,XHt[:,None]))
    CF=crps(yt,fit_pred(np.c_[XH,XF],y,np.c_[XHt,XFt]))
    return {"rho_endo":(C0-CH)/C0,"rho_exo":(CH-CF)/C0}
ns=[int(x) for x in sys.argv[1].split(",")]; reps=int(sys.argv[3]) if len(sys.argv)>3 else 5
fn="out/consistency.json"
try: res=json.load(open(fn))
except Exception: res={"true":TRUE,"runs":{}}
for n in ns:
    out=[one(n) for _ in range(reps)]; res["runs"].setdefault(str(n),[]).extend(out)
    e=np.array([o["rho_endo"] for o in res["runs"][str(n)]]); x=np.array([o["rho_exo"] for o in res["runs"][str(n)]])
    print(f"n={n:6d} reps={len(e)} | endo {e.mean():.4f} (bias {e.mean()-TRUE['rho_endo']:+.4f}, sd {e.std(ddof=1):.4f}) | exo {x.mean():.4f} (bias {x.mean()-TRUE['rho_exo']:+.4f}, sd {x.std(ddof=1):.4f})",flush=True)
json.dump(res,open(fn,"w"),indent=2)
print("TRUE:",{k:round(v,4) for k,v in TRUE.items()})
