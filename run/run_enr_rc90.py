import json, sys
from model_core import run_domain_enriched
import load_dkasc as L, dkasc_rc
s=sys.argv[1]
r=run_domain_enriched(s, dkasc_rc.load(s,"D"), "D",7, L.EXO, n_est=150, nboot=300)
r["note"]="target drift-corrected (trailing 90-day 99th percentile)"
json.dump(r,open(f"out/enr_{s}.json","w"),indent=2)
