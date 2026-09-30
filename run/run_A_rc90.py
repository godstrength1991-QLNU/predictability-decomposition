import json, sys, os, numpy as np
import model_core as M
M.QLEVELS=np.round(np.arange(0.05,0.96,0.05),3)   # horizon-A configuration: 19 levels
from model_core import run_domain
import load_dkasc as L, dkasc_rc
s=sys.argv[1]; path="out/rho_A.json"
res=[x for x in (json.load(open(path)) if os.path.exists(path) else []) if x["domain"]!=s]
r=run_domain(s, dkasc_rc.load(s,"h"), "h",24, L.EXO, daytime_only=True, subsample_origin=72, n_est=200)
r["note"]="drift-corrected target"; res.append(r); json.dump(res,open(path,"w"),indent=2)
