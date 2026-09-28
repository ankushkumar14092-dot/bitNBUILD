# Freight forecasting ML

```text
ml/
├── data/raw/                 # Original downloaded datasets
├── models/                   # Trained model files
├── freight_forecast_training.ipynb # Explore, train, and evaluate the model
├── requirements.txt          # Python dependencies
└── results.json              # Latest training metrics
```

Install dependencies and open the notebook:

```bash
python -m pip install -r requirements.txt
jupyter notebook freight_forecast_training.ipynb
```

Run the notebook cells from top to bottom to train and save the model. The
notebook is split into small steps: load each dataset, inspect and clean it,
align the useful dates, create features, train, compare with a baseline, then
save the model and results. The executed notebook includes the latest outputs.

The current BDI file is a global index proxy from 1985–2009, not an India-route
freight-rate history. Its model is for pipeline development only.

For the full project history and limitations, see [documentation](../documentation.md).
For the proposed backend, frontend, and data flow, see [architecture](../architecture.md).

## AIS congestion demo

`ais_congestion_training.ipynb` is a separate, step-by-step next-hour congestion
demo. It reads NOAA daily `.csv.zst` files placed in `data/raw/`, filters a
small U.S. port area while reading in chunks, builds an AIS-derived congestion
index, joins hourly local weather, then compares Linear Regression, Random
Forest, XGBoost, and LightGBM against a persistence baseline. Weather inputs
are `prjc1h2024.nc` (wind and gust at Los Angeles Pier J) and
`46253h2024.txt.gz` (waves and water temperature at nearby San Pedro South).
Place these beside the AIS files in `data/raw/`. `xarray` is included in
`requirements.txt` for reading the Pier J NetCDF file. Install dependencies
with the same requirements command above and run this notebook from the `ml/`
folder.

The NOAA data is U.S.-focused. The notebook's sample area is Los Angeles, and
its target is a rule-based AIS proxy rather than observed demurrage. The latest
one-week holdout gives Linear Regression MAE 0.685 and RMSE 0.854 on the 0–100
index; persistence MAE is 0.679. In this run, adding weather did not improve on
the persistence baseline. Treat the result as a hackathon method demo, not as
an India-port prediction model.
