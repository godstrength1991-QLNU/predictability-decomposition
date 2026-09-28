#!/usr/bin/env bash
# Reproduce the B8 analysis. Run from the repo root AFTER placing raw data
# (see DATA.md) and adjusting path constants in src/load_*.py.
# The scripts import from src/ and run/, so we expose them on PYTHONPATH.
set -e
export PYTHONPATH="$PWD/src:$PWD/run:$PWD/figures:$PYTHONPATH"
mkdir -p out
# seed out/ with shipped precomputed results so figures can be regenerated
# without re-running the models (delete this line to force a full recompute):
cp -n results/*.json results/*.csv out/ 2>/dev/null || true
echo "== cache raw -> daily/hourly =="
python run/cache_dkasc.py
python run/cache_reservoir_full.py
python run/cache_hkust_full.py
python run/cache_kelmarsh.py
# CAMELS cache is built by src/load_camels.py's __main__:
python src/load_camels.py
echo "== enriched metrics (rho + redundancy + bootstrap) per domain =="
for d in reservoir camels hkust DKASC_site13 DKASC_site31 DKASC_M9; do python run/run_enr.py $d; done
python run/run_enr_kelmarsh.py 2>/dev/null || python run/run_kelmarsh.py
echo "== secondary experiments =="
python run/run_A_all.py                # intraday horizon (solar)
python run/run_sweep.py 1 3 7 14 30    # CAMELS horizon sweep
for d in reservoir kelmarsh M9; do python run/run_capacity.py $d; done
python run/run_perseries.py hkust 34
python run/run_perseries.py camels 30
echo "== figures =="
python figures/make_figs.py
python figures/make_fig_horizon.py
python figures/make_schematic.py
python figures/make_perseries_fig.py
python figures/make_ga.py
echo "done."
