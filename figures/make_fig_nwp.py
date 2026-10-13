"""Figure: share of the perfect-forecast value retained by real NWP forecasts, by lead time
(DKASC Site 13 and Site 31 pooled; raw and bias-corrected ECMWF and GFS)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'font.family':'sans-serif','font.sans-serif':['DejaVu Sans','Arial','Helvetica']})
import matplotlib.pyplot as plt
S=json.load(open("out/nwp_summary.json"))["retained_by_lead"]
L=np.arange(1,8)
fig,ax=plt.subplots(figsize=(3.31,3.6))                      # 84 mm single column
def series(k): return np.array([S[str(l)][k]*100 for l in L])
ax.plot(L,series("gfs_bc"),"o-",color="#2166ac",lw=1.4,ms=4,label="GFS, bias-corrected")
ax.plot(L,series("gfs"),"o--",color="#2166ac",lw=1,ms=3,mfc="white",label="GFS, raw")
e=series("ecmwf_bc"); er=series("ecmwf")
ax.plot(L[:5],e[:5],"s-",color="#b2182b",lw=1.4,ms=4,label="ECMWF, bias-corrected")
ax.plot(L[:5],er[:5],"s--",color="#b2182b",lw=1,ms=3,mfc="white",label="ECMWF, raw")
ax.axhline(0,color="0.6",lw=0.8); ax.set_xticks(L); ax.set_ylim(-10,60)
ax.set_xlabel("lead time (days)",fontsize=8); ax.set_ylabel("retained value (%)",fontsize=8)
ax.tick_params(labelsize=8); ax.grid(alpha=0.25); ax.legend(fontsize=6.5,loc="upper center",bbox_to_anchor=(0.5,-0.24),ncol=1,frameon=False)
plt.tight_layout(); plt.savefig("out/_fig_nwp.pdf",bbox_inches="tight")
