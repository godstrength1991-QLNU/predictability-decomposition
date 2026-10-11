# Predictability decomposition for environmental time series

Code, results and data for the paper **"Decomposing environmental predictability into
endogenous and exogenous components: theory, estimation and cross-domain evidence"**
(Q. Gao, 2026).

## What it does
With a **single fixed probabilistic estimator** whose *inputs alone* are varied and a
**climatology-normalised CRPS**, it decomposes a task's predictability into

- `rho_endo = (CRPS_clim - CRPS_hist)/CRPS_clim` — value of the target's history (endogenous),
- `rho_exo  = (CRPS_hist - CRPS_full)/CRPS_clim` — marginal value of a perfect future forecast (exogenous),
- `persist_share = (CRPS_clim - CRPS_persist)/CRPS_clim` — share explained by persistence,
- `redundancy R` — standalone minus marginal forecast value, split into a composition and an
  interaction term; under the log score `R = I(Y;X_H;X_F)` (interaction information).

Applied to five domains (reservoir storage, CAMELS streamflow, DKASC desert PV, HKUST subtropical
PV, Kelmarsh wind): reservoir storage is inertia-dominated, wind and solar power are
forcing-dominated, and streamflow lies in between.

## New in v1.3.0
| Analysis | Script | Results |
|---|---|---|
| Refit variability (5 seeds per domain) and total uncertainty | `run/run_refit.py` | `results/refit_*.json`, `refit_summary.json` |
| Second estimator family (linear quantile regression) | `run/run_linqr.py` | `results/linqr_*.json`, `linqr_summary.json` |
| Operational forecasts (ECMWF, GFS; raw and bias-corrected) | `run/run_nwp.py` | `results/nwp_*.json`, `nwp_summary.json` |
| Finite-sample consistency of the estimator | `run/run_consistency.py` | `results/consistency.json` |
| Non-Gaussian validation (CRPS gain vs mutual information) | `run/run_nongauss.py` | `results/nongauss.json` |
| Figures for the above | `figures/make_fig_nwp.py`, `make_fig_consistency.py`, `make_fig_nongauss.py` | — |
| Audits of every table and text number | `run/audit_tables_serra.py`, `audit_text_serra.py` | — |

`data/nwp/` holds the archived operational forecasts for the DKASC site (Open-Meteo Previous
Runs API, CC BY 4.0; see `data/nwp/README.md`). `results/PROVENANCE.md` maps every table and
figure of the paper to its result files.

## Layout
```
src/      loaders (one per domain), model_core.py (the engine), dkasc_rc.py (drift correction)
run/      cache_*.py (raw -> cached series) and run_*.py (all analyses), audit_*.py
figures/  make_*.py (all figures)
results/  precomputed results (JSON) and PROVENANCE.md
data/nwp/ archived operational forecasts (Open-Meteo, CC BY 4.0)
```
`src/model_core.py` is domain-agnostic: `build_samples`, `_fit_predict_crps`,
`run_pooled` / `run_domain` and `run_pooled_enriched` / `run_domain_enriched`
(5 configurations + redundancy + block bootstrap).

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

Each `figures/make_*.py` script regenerates one figure of the paper from `results/`.

## Cite
Gao, Q. (2026). Decomposing environmental predictability into endogenous and exogenous
components: theory, estimation and cross-domain evidence. Manuscript.

Code: Gao, Q. (2026). predictability-decomposition. Zenodo.
https://doi.org/10.5281/zenodo.23016533

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23016533.svg)](https://doi.org/10.5281/zenodo.23016533)

## License
MIT (see `LICENSE`).
