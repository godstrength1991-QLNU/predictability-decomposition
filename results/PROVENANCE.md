# Provenance of every number in the manuscript

All values are read from the files in this folder; none are typed by hand.

| Manuscript item | Source file(s) | Configuration |
|---|---|---|
| Table 2 (predictability by domain, 95% CI; DKASC drift-corrected, Eq. 21) | `enr_reservoir.json`, `enr_camels.json`, `enr_DKASC_site13.json`, `enr_DKASC_site31.json`, `enr_DKASC_M9.json`, `enr_hkust_norm.json` (HKUST, capacity-normalised), `enr_kelmarsh.json` | horizon B (daily, H=7), 13 quantile levels, 150 trees, 300 block-bootstrap replicates |
| Table 3 (forecast value, redundancy with CI, composition/interaction) | same `enr_*.json` (ci_redu); composition and interaction in `shapley_attribution.json`; HKUST raw pooled row: `enr_hkust.json` | as above |
| Table 4 (permutation entropy) | `permutation_entropy.json` | order 4, delay 1, median over series |
| Table 5 (rolling-origin evaluation) | `rolling_reservoir.json`, `rolling_site13.json`, `rolling_site31.json`, `rolling_M9.json`, `rolling_kelmarsh.json` | three consecutive test blocks, primary configuration |
| Table 6 (drift correction) | uncorrected: `enr_DKASC_*_uncorrected.json`; 365-day window: `enr_DKASC_*_rollcap.json`; 90-day window: `enr_DKASC_*.json` | trailing 99th percentile of past output |
| Table 7 (robustness) | Scheme 1, 25 dams: `fork_check.json`; Scheme 2, 25 dams: `rho_reservoir_matched.json`; Scheme 2, 403 dams: `rho_reservoir_full.json`; HKUST 18 sites: `rho_hkust_18.json`; HKUST 58 sites: `rho_hkust_full.json` | all rows: 19 quantile levels, 200 trees |
| Section 4.9 text, order-symmetric (Shapley) attribution | `shapley_attribution.json` (derived from the `enr_*.json` values) | horizon B |
| Table 8 (capacity robustness) | `cap_reservoir.json`, `cap_M9.json` (drift-corrected), `cap_kelmarsh.json` | weak 50 trees/8 leaves, medium 150/31, strong 400/63 |
| Table 9 (appendix, raw CRPS) | `enr_*.json` (CRPS_clim, CRPS_climfut, CRPS_persist, CRPS_hist, CRPS_full) | horizon B |
| Fig. 1 (synthetic validation) | `synth_results.npz` (me, ce, mx, cx) | linear-Gaussian, Monte Carlo N = 2e5 |
| Theory text, KSG robustness (sin rho = 0.89, MI 0.17-0.19) | `ksg_results.npz` | KSG estimator |
| Theory text, KSG tanh/cubic rho = 1.00 | `ksg_v3_rerun_log.txt` (output of the original `ksg_v3.py`) | KSG estimator |
| Fig. 2 (framework) | schematic; bar heights illustrative, not data | - |
| Fig. 3 (predictability plane) | `rho_B.json` (= enr_* values, HKUST capacity-normalised); arrows: `rho_A.json`; faded HKUST point: `enr_hkust.json` | horizon A: hourly, H=24, 19 quantiles, 200 trees, one origin per 72 h |
| Fig. 4 (horizon dependence) | `camels_sweep.json` | 19-basin subset (every fifth of 92), 150 trees |
| Fig. 5 (forecast value) | `rho_B.json` | horizon B |
| Fig. 6 (imperfect forecast), Eq. (22) | `degrade_kelmarsh.json`, `degrade_DKASC_site13.json`, `degrade_hkust.json`, `degrade_DKASC_M9.json`, `degrade_DKASC_site31.json`, `degrade_camels.json` | horizon B primary configuration; Gaussian forcing errors lambda in {0, 0.25, 0.5, 1}, seed 0 |
| Fig. 7 (within-domain) | `perseries_hkust.json` (34 sites), `perseries_camels.json` (30 basins) | single series, 7 quantiles, 40 trees, 16 leaves |
