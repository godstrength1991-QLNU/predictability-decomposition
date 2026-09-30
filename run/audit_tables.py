import json, re
J=lambda f: json.load(open(f"out/{f}.json"))
tex=open("merge/B8_full_manuscript.tex").read()
def table(label):
    m=re.search(r"\\label\{"+label+r"\}.*?\\midrule(.*?)\\bottomrule",tex,re.S); return m.group(1)
def nums(s): return [float(x.replace("$-$","-").replace("−","-")) for x in re.findall(r"\$?-?\$?-?\d+\.\d+",s.replace("$-$","-").replace("$",""))]
issues=[]
def chk(name,got,exp,tol=0.0051):
    if abs(got-exp)>tol: issues.append(f"{name}: manuscript {got} vs source {exp:.4f}")
B={r["domain"]:r for r in J("rho_B")}
rows={"Reservoir (403":"Reservoir(ASOS-net)","CAMELS":"CAMELS(streamflow)","HKUST (58":"HKUST(subtropical PV)","M9":"DKASC_M9","Site~31":"DKASC_site31","Site~13":"DKASC_site13","Kelmarsh":"Kelmarsh(wind)"}
# Table 2
for line in table("tab:main").strip().split("\\\\"):
    for k,d in rows.items():
        if k in line:
            v=nums(line.split("&",2)[2]); r=B[d]
            for got,exp,n in zip(v,[r["persist_share"],r["rho_endo_c"],*r["ci_endo"],r["rho_exo_c"],*r["ci_exo"]],["p_shr","endo","ci_lo","ci_hi","exo","ci_lo","ci_hi"]): chk(f"T2 {d} {n}",got,exp)
# Table 3
sh={r["domain"]:r for r in J("shapley_attribution")["rows"]}
for line in table("tab:redundancy").strip().split("\\\\"):
    src=None
    if "raw pooled" in line: src=J("enr_hkust")
    else:
        for k,d in rows.items():
            if k in line: src=B[d]
    if not src: continue
    v=nums(line.split("&",1)[1])
    comp=src["rho_endo_c"]*src["exo_given_clim"]
    exp=[src["exo_given_clim"],src["rho_exo_c"],src["redundancy"],*src["ci_redu"],comp,src["redundancy"]-comp]
    for got,e_,n in zip(v,exp,["exo|clim","exo","R","ci_lo","ci_hi","comp","inter"]): chk(f"T3 {src['domain']} {n}",got,e_)
    fr=re.findall(r"(-?\d+)\\%",line.replace("$-$","-"))
    if fr: chk(f"T3 {src['domain']} fraction%",float(fr[0]),src["redundancy_frac"]*100,0.51)
# Table 4
pe={r["domain"]:r for r in J("permutation_entropy")["rows"]}
for line in table("tab:pe").strip().split("\\\\"):
    for k,d in rows.items():
        if k in line:
            v=nums(line.split("&",1)[1]); p=pe[d]
            chk(f"T4 {d} PE",v[0],p["PE"],0.0006); chk(f"T4 {d} endo",v[1],B[d]["rho_endo_c"]); chk(f"T4 {d} exo",v[2],B[d]["rho_exo_c"]); chk(f"T4 {d} tot",v[3],B[d]["rho_endo_c"]+B[d]["rho_exo_c"])
# Table 5 rolling
rk={"Reservoir":"reservoir","Site~13":"site13","Site~31":"site31","M9":"M9","Kelmarsh":"kelmarsh"}
for line in table("tab:rolling").strip().split("\\\\"):
    for k,f in rk.items():
        if k in line:
            v=nums(line.split("&",1)[1]); bb=sorted(J(f"rolling_{f}")["blocks"],key=lambda b:b["block"])
            exp=[x for b in bb for x in (b["rho_endo"],b["rho_exo"])]
            for i,(g,e_) in enumerate(zip(v,exp)): chk(f"T5 {f} #{i}",g,e_)
# Table 6 drift
for line in table("tab:drift").strip().split("\\\\"):
    for k,d in [("Site~13","DKASC_site13"),("Site~31","DKASC_site31"),("M9","DKASC_M9")]:
        if k in line:
            v=nums(line.split("&",1)[1]); u=J(f"enr_{d}_uncorrected"); w=J(f"enr_{d}_rollcap")
            exp=[u["rho_endo_c"],u["rho_exo_c"],w["rho_endo_c"],w["rho_exo_c"],B[d]["rho_endo_c"],B[d]["rho_exo_c"]]
            for i,(g,e_) in enumerate(zip(v,exp)): chk(f"T6 {d} #{i}",g,e_)
# Table 7 robustness
T7=nums(table("tab:robust"))
fc={r["domain"]:r for r in J("fork_check")}["Reservoir(ASOS-net)"]; mt=J("rho_reservoir_matched"); fu=J("rho_reservoir_full"); h18=J("rho_hkust_18"); h58=J("rho_hkust_full")
exp=[]
for r in [fc,mt,fu,h18,h58]: exp+= [r["persist_share"],r["rho_endo_c"],r["rho_exo_c"]]
for i,(g,e_) in enumerate(zip(T7,exp)): chk(f"T7 #{i}",g,e_)
# Table 8 capacity
for line in table("tab:capacity").strip().split("\\\\"):
    for k,f in [("Reservoir","reservoir"),("M9","M9"),("Kelmarsh","kelmarsh")]:
        if k in line:
            v=nums(line.split("&",1)[1]); exp=[x for c in J(f"cap_{f}") for x in (c["rho_endo_c"],c["rho_exo_c"])]
            for i,(g,e_) in enumerate(zip(v,exp)): chk(f"T8 {f} #{i}",g,e_)
# Table 9 raw CRPS (appendix)
t9=table("tab:raw")
m9={"Reservoir":"enr_reservoir","CAMELS":"enr_camels","Site~13":"enr_DKASC_site13","Site~31":"enr_DKASC_site31","M9":"enr_DKASC_M9","HKUST":"enr_hkust_norm","Kelmarsh":"enr_kelmarsh"}
for line in t9.strip().split("\\\\"):
    for k,f in m9.items():
        if k in line:
            v=nums(line.split("&",2)[2]); r=J(f)
            exp=[r["CRPS_clim"],r["CRPS_climfut"],r["CRPS_persist"],r["CRPS_hist"],r["CRPS_full"]]
            for g,e_,n in zip(v,exp,["clim","climfut","persist","hist","full"]):
                if abs(g-e_)>max(0.0051,abs(e_)*0.006): issues.append(f"T9 {f} {n}: manuscript {g} vs source {e_:.4f}")
print("TABLE ISSUES:",len(issues)); [print("  ",i) for i in issues]
