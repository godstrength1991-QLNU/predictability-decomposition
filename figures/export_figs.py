"""Export all manuscript figures (Fig 1-7) as vector PDF + >=1000 dpi TIFF.
Run from the repository root after the results are in out/."""
import runpy, os, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams['pdf.fonttype']=42
import matplotlib.pyplot as plt
OUT="out/figures_final"; os.makedirs(OUT,exist_ok=True)
captured=[]; _orig=plt.savefig
def cap(*a,**k):
    f=plt.gcf()
    if f not in captured: captured.append(f)
plt.savefig=cap; _close=plt.close; plt.close=lambda *a,**k: None
jobs=[("figures/make_fig1_synthetic.py",["Fig1_synthetic_validation"]),
      ("figures/make_schematic.py",["Fig2_framework"]),
      ("figures/make_figs.py",["Fig3_predictability_plane","Fig5_redundancy"]),
      ("figures/make_fig_horizon.py",["Fig4_horizon_dependence"]),
      ("figures/make_perseries_fig.py",["Fig7_within_domain"]),
      ("figures/make_fig_degradation.py",["Fig6_imperfect_forecast"])]
for script,names in jobs:
    captured.clear(); runpy.run_path(script)
    assert len(captured)>=len(names), (script,len(captured))
    for fig,nm in zip(captured,names):
        fig.savefig(f"{OUT}/{nm}.pdf")
        w_in=fig.get_size_inches()[0]; _dpi=max(1010,int(7.48*1000/w_in)+10)
        fig.savefig(f"{OUT}/{nm}.tiff",dpi=_dpi,pil_kwargs={"compression":"tiff_lzw"})
        fig.savefig(f"{OUT}/{nm}.png",dpi=300)
        w,h=fig.get_size_inches(); print(f"{nm:30s} TIFF dpi {_dpi}; effective dpi at 190 mm = {int(w*_dpi/7.48)}")
