# Data

The loaders expect each raw dataset under `data/` (or the paths set at the top of
each `src/load_*.py`; edit the `UP`/path constants to match your machine).

| Domain | Source | Access |
|---|---|---|
| Reservoir storage + ASOS meteorology | RAWRIS (KRC) + KMA ASOS | RAWRIS storage is **not publicly redistributable**; ASOS daily records are public (KMA). Place `mawp_dataset.pkl` and `ASOS_weather_*.csv` under `data/reservoir/`. |
| CAMELS streamflow + forcing | Newman et al. 2015, HESS 19:209-223, doi:10.5194/hess-19-209-2015 (dataset doi:10.5065/D6MW2F4D) | Download `basin_timeseries_v1p2_metForcing_obsFlow.zip`; place `basin_mean_forcing/daymet/<HUC>/` and `usgs_streamflow/<HUC>/` under `data/camels/forcing/` and `data/camels/streamflow/`. |
| DKASC desert solar | Desert Knowledge Australia Centre, Alice Springs, http://dkasolarcentre.com.au/download | Per-site 5-min CSVs (also on Kaggle); place the zips under `data/dkasc/`. |
| HKUST subtropical rooftop PV | Lin et al. 2025, Scientific Data 12:63, doi:10.1038/s41597-025-04397-y (Dryad doi:10.5061/dryad.m37pvmd99) | Nested `Dataset.zip` (meteorology + per-site generation). |
| Kelmarsh wind | Plumley 2022, Zenodo doi:10.5281/zenodo.8252025 (CC-BY) | Per-year SCADA zips; place under `data/kelmarsh/`. |

Aggregation (all domains): raw sub-daily records are cleaned (sensor sentinels,
coverage >= 80% per bin) and aggregated to the daily/hourly grids used in the paper.
