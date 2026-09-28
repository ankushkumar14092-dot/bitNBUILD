"""Inference adapter for the trained Brent crude market proxy."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "ml_assets"
MODEL_PATH = ASSET_DIR / "models" / "brent_proxy_model.joblib"
DATA_PATH = ASSET_DIR / "data" / "brent-daily.csv"
RESULTS_PATH = ASSET_DIR / "models" / "brent_proxy_evaluation.json"


def _make_features(prices: pd.Series) -> pd.DataFrame:
    frame = pd.DataFrame(index=prices.index)
    for lag in (1, 2, 5, 10, 20, 60):
        frame[f"price_lag_{lag}"] = prices.shift(lag)
    returns = prices.pct_change()
    for window in (5, 20, 60):
        frame[f"return_{window}"] = prices.pct_change(window)
        frame[f"volatility_{window}"] = returns.rolling(window).std()
    frame["year_sin"] = np.sin(2 * np.pi * frame.index.dayofyear / 365.25)
    frame["year_cos"] = np.cos(2 * np.pi * frame.index.dayofyear / 365.25)
    return frame.replace([np.inf, -np.inf], np.nan)


def predict_market_proxy() -> dict:
    if not all(path.exists() for path in (MODEL_PATH, DATA_PATH, RESULTS_PATH)):
        raise FileNotFoundError("Open backend/ml_assets/models/train_market_proxy.ipynb and run all cells to train the market proxy.")

    bundle = joblib.load(MODEL_PATH)
    raw = pd.read_csv(DATA_PATH)
    prices = pd.Series(
        pd.to_numeric(raw["Price"], errors="coerce").to_numpy(),
        index=pd.to_datetime(raw["Date"], errors="coerce"),
        name="brent_usd_per_barrel",
    ).dropna().sort_index().loc[lambda values: ~values.index.duplicated(keep="last")]
    features = _make_features(prices).dropna()
    latest_date = prices.index[-1]
    latest = prices.loc[latest_date]
    row = features.loc[[latest_date], bundle["feature_columns"]]
    predicted = float(bundle["model"].predict(row)[0])
    evaluation = json.loads(RESULTS_PATH.read_text())

    return {
        "status": "prototype_only",
        "model": "brent_crude_proxy_ridge",
        "target": "Brent crude oil spot price proxy, not marine bunker fuel or a freight rate",
        "unit": "USD/barrel",
        "as_of": latest_date.date().isoformat(),
        "horizon_observations": int(bundle["horizon_observations"]),
        "latest_observed_price": round(float(latest), 2),
        "predicted_price": round(predicted, 2),
        "persistence_baseline_price": round(float(latest), 2),
        "backtest": evaluation["holdout"],
        "beats_persistence_baseline": evaluation["holdout"]["candidate_beats_persistence"],
        "recommended_for_decision_use": False,
        "limitations": evaluation["limitations"],
    }
