# B8 — Predictability decomposition for environmental time series

Code for the paper **"When does data-driven forecasting fail? A
predictability-decomposition framework separating endogenous inertia from
exogenous forcing in environmental time series"** (Q. Gao, under review,
*Environmental Modelling & Software*, 2026).

## What it does
With a **single fixed probabilistic estimator** (LightGBM quantile regression)
whose *inputs alone* are varied, and a **climatology-normalised CRPS**, it
decomposes a task's predictability into

- `rho_endo = (CRPS_clim - CRPS_hist)/CRPS_clim` — value of the target's history (endogenous),
- `rho_exo  = (CRPS_hist - CRPS_full)/CRPS_clim` — marginal value of a perfect future forecast (exogenous),
- `persist_share = (CRPS_clim - CRPS_persist)/CRPS_clim` — share explained by persistence,
- `redundancy R` — standalone minus marginal forecast value (via the extra `climfut` model);
  under the log score, `R = I(Y;X_H;X_F)` (interaction information).

Five domains (reservoir storage, CAMELS streamflow, DKASC desert PV, HKUST
subtropical PV, Kelmarsh wind) place every task on a continuous inertia-to-forcing
spectrum; block-bootstrap gives 95% intervals.

## Layout
```
src/      loaders (one per domain) + model_core.py (the engine)
run/      cache_*.py (raw -> cached daily/hourly) and run_*.py (compute rho / enriched / sweeps)
figures/  make_*.py (Fig 1-6, graphical abstract)
results/  precomputed rho_*.json, enr_*.json, sweeps, rho_results.csv
```
`src/model_core.py` is domain-agnostic: `build_samples`, `_fit_predict_crps`,
`run_pooled` / `run_domain` (4 configs) and `run_pooled_enriched` /
`run_domain_enriched` (5 configs + redundancy + bootstrap).

## Install
```
python -m pip install -r requirements.txt
```

## Data
See `DATA.md`. Loaders read raw files from paths set at the top of each
`src/load_*.py` (a research archive: adjust those path constants to your machine).
The reservoir storage series (RAWRIS) are not publicly redistributable; all other
datasets are open (DOIs in `DATA.md`).

## Set up data
Run `bash setup_dirs.sh` to create the `data/` tree, then place each downloaded
dataset in its folder (see `DATA.md`). Alternatively, edit the path constant at
the top of each `src/load_*.py`.

To only regenerate the figures from the shipped `results/`, no raw data is
needed: `mkdir -p out && cp results/*.json results/*.csv out/ && python figures/make_figs.py`.

## Reproduce
With data in place: `bash reproduce.sh` (caches each domain, computes the
enriched metrics, runs the horizon sweep / capacity / per-series checks, and
rebuilds the figures). Precomputed `results/` are included so the figures can be
regenerated without re-running the models.

## Cite
Gao, Q. (2026). When does data-driven forecasting fail? ... *Environmental
Modelling & Software* (under review). Code archived at Zenodo: <DOI on acceptance>.

## License
MIT (see `LICENSE`).
