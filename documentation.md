# CARGO-PILOT project documentation

## Project goal

CARGO-PILOT is a decision-support prototype for importing dry bulk cargo into East Coast India. It is intended to help a procurement team compare freight, vessel, timing, port-risk, and landed-cost options. The target ports include Paradip, Visakhapatnam, Kolkata/Haldia, and Chennai.

The intended system flow is:

1. Load and validate market and operations data.
2. Forecast freight and estimate operational risk.
3. Compare chartering and arrival scenarios by landed cost.
4. Explain the recommendation and flag uncertain cases for human review.

## Current project status

The ML exploration and training notebooks exist and have been executed. They are designed for a beginner: loading, cleaning, feature creation, training, evaluation, and saving are separated into small explained cells.

The backend API (FastAPI) and frontend dashboard (React/Vite) have been built and restructured into `backend/` and `frontend/` directories. The BDI freight-rate model is a learning prototype, not a validated route-level forecasting service; its test error is worse than the simple persistence baseline. A separate AIS congestion model now runs on a small U.S. sample, but it is a method demo, not an India-port model. Neither model should support real procurement decisions.

## Files and folders

```text
.
├── architecture.md            # Proposed end-to-end system design
├── documentation.md           # Work completed, data, training, and limitations
├── README.md                  # Project overview and setup instructions
├── frontend/                  # React/Vite dashboard application
├── backend/                   # FastAPI server and calculation logic
├── tests/                     # Separated frontend and backend tests
└── ml/                        # ML models, training scripts, and notebooks
    ├── data/raw/              # Local source CSV files
    ├── models/                # Locally saved trained model
    ├── freight_forecast_training.ipynb
    ├── ais_congestion_training.ipynb
    ├── ml_forecast.py         # Prediction adapters for backend
    ├── requirements.txt
    ├── results.json           # Latest evaluation and source coverage
    ├── README.md
    └── .gitignore
```

Raw data and saved model files are ignored by Git in `ml/.gitignore`. They stay on the local machine unless the ignore rules are changed. Check source licensing before sharing them.

## Data loaded so far

The notebook loads each source, shows sample rows, checks columns and date coverage, and then decides whether the source can be used in the freight training set.

| Dataset | Local file | How it is used | Coverage and caveat |
|---|---|---|---|
| Baltic Dry Index (BDI) | `ml/data/raw/bdi_historical_1985_2009.csv` | Global dry-bulk market proxy and prediction target | 1985-01-04 to 2009-03-13. This is a community mirror with unverified redistribution terms. It is not an India route quote. |
| Brent crude oil | `ml/data/raw/brent-daily.csv` | Fuel-cost proxy and a model input | EIA Brent spot price in USD/barrel. Crude is not marine bunker fuel. The notebook joins by using the most recent Brent observation on or before each BDI date. |
| India daily rainfall | `ml/data/raw/daily-rainfall-at-state-level.csv` | Loaded and filtered for Odisha, West Bengal, Andhra Pradesh, and Tamil Nadu for future port-risk work | 2009-01-01 to 2023-12-26 in the downloaded file. State-level rainfall is not a direct port-congestion or demurrage label. Its overlap with the BDI data is too short to use in the current freight model. |
| NOAA AIS 2024 | `ml/data/raw/ais-2024-01-01.csv.zst` through `ais-2024-01-07.csv.zst` | Seven-day sample used for hourly vessel features and a congestion-method demo | U.S.-focused data, filtered to San Pedro Bay / Los Angeles. Not East Coast India traffic and has no observed congestion or demurrage label. Compressed source files are excluded from Git. |
| NOAA NDBC Pier J weather | `ml/data/raw/prjc1h2024.nc` | Hourly wind speed and gust features for the AIS demo | Los Angeles Pier J observation station; nearby to, but not identical with, every AIS position. |
| NOAA NDBC San Pedro South buoy | `ml/data/raw/46253h2024.txt.gz` | Hourly wave height, dominant/average wave periods, and water temperature for the AIS demo | Nearby buoy, not a port-wide weather field. Missing-value sentinels are removed before hourly aggregation. |

The BDI Kaggle source shown in the roadmap has not been loaded. The available BDI CSV is a substitute global index series, and its license still needs verification. The exact route-specific target data remains missing.

### Why the other suggested datasets were not included

- U.S. AIS data has the wrong geography for Indian ports; the separate AIS notebook is a clearly labeled method demo only.
- Generic or retail inventory data cannot represent coal-plant stock or consumption ground truth.
- General supply-chain disruption data may be synthetic or outside dry-bulk shipping; it can support interface experiments, but should not be treated as actual port events.
- UNCTAD annual trade data is useful background context but too aggregated to label daily or weekly voyage rates.
- India rainfall is retained for future risk analysis, but cannot be joined usefully to this old BDI series.

## Data source notes

- The Brent CSV is based on the U.S. Energy Information Administration Europe Brent spot-price series. The notebook records its source and treats it as a proxy, not as bunker fuel.
- The India rainfall file is from the India Data Portal / India-WRIS resource and is marked Open Data Commons Attribution. Preserve attribution if using it.
- The BDI file is from a community GitHub mirror. Verify redistribution rights before sharing or deploying it.
- The notebook records the retrieval date as 2026-09-27. It also prints the file's observed start and end dates so that the values are visible rather than inferred from a listing title.

## How the notebook works

Open `ml/freight_forecast_training.ipynb` and run cells from top to bottom.

1. Imports Python packages and finds the project data directory.
2. Checks that the three expected CSV files exist.
3. Loads and inspects BDI, Brent, and rainfall independently.
4. Cleans dates and numeric columns and filters rainfall to states containing target ports.
5. Aligns BDI and Brent dates using backward matching, which avoids using a future oil value.
6. Builds BDI lag, rolling average, rolling variability, and percentage-change features. It also builds Brent lag and percentage-change features and calendar-season features.
7. Creates a target equal to the BDI value five observations later.
8. Splits observations chronologically: the first 80% trains the model and the later 20% evaluates it. Rows are not shuffled.
9. Trains `HistGradientBoostingRegressor` and compares it with a persistence baseline. The baseline predicts that the future BDI will equal the current BDI.
10. Saves the candidate model and writes the metrics and limitations to `ml/results.json`.

Rainfall is deliberately inspected but not joined to training. It starts near the end of the available BDI series, so including it would leave too few training observations.

## Latest training result

The latest scores are in `ml/results.json`. At the last recorded run:

| Method | MAE (BDI points) | RMSE (BDI points) | MAPE |
|---|---:|---:|---:|
| Gradient boosting candidate | 1,312.77 | 2,108.35 | 22.33% |
| Persistence baseline | 251.27 | 381.34 | 5.93% |

Lower error is better. The candidate loses to persistence on this holdout. The notebook marks it `recommended_for_decision_use: false`. Saving a model file means training ran; it does not mean the model is accurate or production-ready.

## Install and run

From the `ml` directory:

```bash
python -m pip install -r requirements.txt
jupyter notebook freight_forecast_training.ipynb
```

Run the notebook from the first cell to the last. It saves:

- `ml/models/bdi_proxy_model.joblib`
- `ml/results.json`

The notebook reads CSVs already present in `ml/data/raw/`. The separate URL downloader was removed because it was not needed for this local notebook workflow.

## What is needed before real freight forecasting

1. Obtain licensed historical rate/fixture data for the relevant origin-destination routes, cargo types, vessel classes, and booking windows.
2. Obtain enough history across seasons. Newly introduced India route indices have a short record, so they alone cannot train a reliable seasonal model yet.
3. Get historical bunker prices, port charges, laytime, waiting time, and demurrage outcomes.
4. Add vessel arrival or port-call history for the target ports, with clear timestamps and vessel classes.
5. Add plant inventory and consumption history if arrival timing is to be optimized.
6. Rebuild and evaluate using route-aware chronological backtests. Compare each candidate to simple baselines before presenting recommendations.

Until these labels exist, present rate and risk outputs as proxies or scenarios with clear uncertainty and human review.

## AIS congestion demo

Open `ml/ais_congestion_training.ipynb` for the separate next-hour congestion workflow. It processes seven NOAA daily files in chunks, keeps messages inside a small Los Angeles bounding box, aggregates hourly vessel count/speed/stationary ratio, adds six hourly weather features from Pier J and the nearby San Pedro South buoy, constructs a 0–100 rule-based congestion index, creates lag and rolling features, and uses a chronological 80/20 split. Linear Regression, Random Forest, XGBoost, and LightGBM are compared with a persistence baseline.

The latest weather-enabled run had 143 usable examples (114 train, 29 test). Linear Regression scored MAE 0.685 and RMSE 0.854 on the constructed index; persistence scored MAE 0.679, so this run's ML candidate did not beat persistence. The earlier AIS-only model performed better on the same small holdout, so weather has not yet shown a benefit here. These scores measure prediction of a self-defined index in one U.S. port area over one week. They do not establish Indian-port accuracy, measured congestion forecasting, or demurrage prediction. Results and artifact are in `ml/ais_congestion_results.json` and `ml/models/ais_congestion_demo.joblib`.
