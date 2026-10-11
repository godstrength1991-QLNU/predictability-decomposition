# Data provenance (SERRA manuscript)

Every number in every table and figure traces to the result files below (folder `results/` unless stated).

| Item | Content | Source |
|---|---|---|
| Fig. 1 | Synthetic validation | synth_results.npz; ksg_results.npz |
| Fig. 2 | Finite-sample error of the estimator | consistency.json; run/run_consistency.py; figures/make_fig_consistency.py |
| Fig. 3 | Non-Gaussian validation | nongauss.json; run/run_nongauss.py; figures/make_fig_nongauss.py |
| Fig. 4 | Framework schematic | illustrative (no data) |
| Fig. 5 | Predictability plane | rho_B.json; rho_A.json; enr_hkust.json |
| Fig. 6 | Horizon dependence | camels_sweep.json |
| Fig. 7 | Forecast value and redundancy | rho_B.json |
| Fig. 8 | Imperfect forecast (Gaussian errors) | degrade_*.json |
| Fig. 9 | Operational forecasts (ECMWF, GFS) | nwp_DKASC_site13.json; nwp_DKASC_site31.json; nwp_summary.json; data/nwp/*.csv; run/run_nwp.py |
| Fig. 10 | Within-domain distributions | perseries_hkust.json; perseries_camels.json |
| Table 1 | Notation | definitions (no data) |
| Table 2 | Decomposition by domain, 95% CI | results/enr_*.json (DKASC drift-corrected; HKUST capacity-normalised); rho_B.json |
| Table 3 | Forecast value, redundancy, composition/interaction | enr_*.json (ci_redu); shapley_attribution.json; enr_hkust.json (raw pooled row) |
| Table 4 | Permutation entropy | permutation_entropy.json; rho_B.json |
| Table 5 | Uncertainty decomposition (refit + bootstrap) | refit_<domain>.json (5 seeds each); refit_summary.json; run/run_refit.py |
| Table 6 | Two estimator families | linqr_<domain>.json; linqr_summary.json; run/run_linqr.py |
| Table 7 | Rolling-origin evaluation | rolling_*.json; run/run_rolling.py |
| Table 8 | Drift correction | enr_DKASC_*_uncorrected.json; enr_DKASC_*_rollcap.json; enr_DKASC_*.json |
| Table 9 | Spatial matching and sample size | fork_check.json; rho_reservoir_matched.json; rho_reservoir_full.json; rho_hkust_18.json; rho_hkust_full.json |
| Table 10 | Estimator capacity | cap_reservoir.json; cap_M9.json; cap_kelmarsh.json |
| Table A.1 | Raw CRPS (appendix) | enr_*.json (CRPS_* fields) |

Text numbers: checked by `run/audit_tables_serra.py` (all tables) and `run/audit_text_serra.py` (42 statements in the text, including all numbers of the estimation, refit, estimator, operational-forecast and non-Gaussian analyses).
