"""Run a figure script with every font size multiplied by K, and save its PDF output(s) to
serra/fig_scaled/<name>.pdf according to MAP. The original script is not modified."""
import sys, os, runpy, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
script, K = sys.argv[1], float(sys.argv[2])
MAP={"quadrant":"Fig5","redundancy":"Fig7","framework":"Fig4","horizon":"Fig6","distributions":"Fig10",
     "_fig7":"Fig8","consistency":"Fig2","nongauss":"Fig3","nwp":"Fig9","synthetic":"Fig1"}
matplotlib.rcParams.update({"font.family":"sans-serif","font.sans-serif":["Liberation Sans","Arial","Helvetica"],
    "mathtext.fontset":"custom","mathtext.rm":"Liberation Sans","mathtext.it":"Liberation Sans:italic","mathtext.bf":"Liberation Sans:bold",
    "mathtext.sf":"Liberation Sans"})
_upd=matplotlib.rcParams.update
def _guard(*a,**kw):                      # keep Arial-metric font even if a script resets the family
    _upd(*a,**kw); matplotlib.RcParams.__setitem__(matplotlib.rcParams,"font.sans-serif",["Liberation Sans","Arial","Helvetica"])
matplotlib.rcParams.update=_guard
matplotlib.rcParams["font.size"]*=K
for k in ["axes.titlesize","axes.labelsize","xtick.labelsize","ytick.labelsize","legend.fontsize"]:
    v=matplotlib.rcParams[k]
    if isinstance(v,(int,float)): matplotlib.rcParams[k]=v*K
_orig=FontProperties.set_size
def set_size(self,size):
    if isinstance(size,(int,float)): size=size*K
    return _orig(self,size)
FontProperties.set_size=set_size
import matplotlib.figure as mf
_save=mf.Figure.savefig
def savefig(self,fname,*a,**kw):
    f=str(fname)
    if f.endswith(".pdf"):
        for key,name in MAP.items():
            if key in os.path.basename(f).lower() or key in f.lower():
                _save(self,f"serra/fig_scaled/{name}.pdf",*a,**{k:v for k,v in kw.items() if k!="dpi"}); break
    os.makedirs(os.path.dirname(f) or ".",exist_ok=True)
    return _save(self,fname,*a,**kw)
mf.Figure.savefig=savefig
plt.savefig=lambda *a,**kw: plt.gcf().savefig(*a,**kw)
sys.argv=[script]; runpy.run_path(script,run_name="__main__")
