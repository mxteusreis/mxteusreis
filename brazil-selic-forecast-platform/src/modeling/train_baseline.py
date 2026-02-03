from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.config import ARTIFACTS_DIR, GOLD_DIR
from src.modeling.forecast import build_lag_matrix, infer_frequency, iterative_forecast
from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline Selic forecaster")
    parser.add_argument("--horizon", type=int, default=30, help="Forecast horizon in days")
    parser.add_argument("--lags", type=int, nargs="+", default=[1, 2, 3, 5])
    return parser.parse_args()


def load_dataset() -> pd.DataFrame:
    dataset_path = GOLD_DIR / "selic_dataset.csv"
    if not dataset_path.exists():
        raise FileNotFoundError("Gold dataset not found. Run feature build first.")
    df = pd.read_csv(dataset_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).sort_values("date")
    return df


def train_model(df: pd.DataFrame, lags: list[int]) -> tuple[LinearRegression, dict]:
    X, y = build_lag_matrix(df["value"], lags)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, preds)),
        "rmse": float(mean_squared_error(y_test, preds, squared=False)),
    }
    return model, metrics


def save_metrics(metrics: dict, output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)


def save_forecast(
    df: pd.DataFrame, model: LinearRegression, horizon: int, lags: list[int]
) -> Path:
    history = df["value"].tolist()
    forecasts = iterative_forecast(model, history, horizon, lags)
    freq = infer_frequency(df["date"])
    future_dates = pd.date_range(df["date"].iloc[-1], periods=horizon + 1, freq=freq)[
        1:
    ]
    forecast_df = pd.DataFrame({"date": future_dates, "forecast": forecasts})
    output_path = ARTIFACTS_DIR / "forecast.csv"
    forecast_df.to_csv(output_path, index=False)
    return output_path


def run(horizon: int, lags: list[int]) -> None:
    df = load_dataset()
    model, metrics = train_model(df, lags)

    model_path = ARTIFACTS_DIR / "selic_baseline.joblib"
    joblib.dump({"model": model, "lags": lags}, model_path)
    logger.info("Saved model to %s", model_path)

    metrics_path = ARTIFACTS_DIR / "metrics.json"
    save_metrics(metrics, metrics_path)
    logger.info("Saved metrics to %s", metrics_path)

    forecast_path = save_forecast(df, model, horizon, lags)
    logger.info("Saved forecast to %s", forecast_path)


if __name__ == "__main__":
    args = parse_args()
    run(args.horizon, args.lags)
