#!/usr/bin/env bash
# Create the data/ tree the loaders expect, then place downloads per DATA.md.
set -e
mkdir -p data/dkasc data/kelmarsh data/reservoir data/hkust \
         data/camels/forcing/03 data/camels/streamflow/03 out
echo "Created data/ tree. Place the downloaded files as follows (see DATA.md):"
echo "  data/dkasc/                 archive.zip, archive__1_.zip, archive__2_.zip"
echo "  data/kelmarsh/              Kelmarsh_SCADA_2019_3085.zip ... 2022_4457.zip"
echo "  data/reservoir/            mawp_dataset.pkl, ASOS_weather_*.csv"
echo "  data/hkust/                Dataset.zip"
echo "  data/camels/forcing/03/    *_lump_cida_forcing_leap.txt"
echo "  data/camels/streamflow/03/ *_streamflow_qc.txt"
