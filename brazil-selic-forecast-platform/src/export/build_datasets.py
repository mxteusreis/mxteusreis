from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import ARTIFACTS_DIR, DATASETS_DIR, GOLD_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

MODEL_VERSION = "baseline-lag-regression-v1"
MODEL_TYPE = "LinearRegression (lags)"
DATA_SOURCE = "BCB SGS"


def load_gold_dataset() -> pd.DataFrame:
    dataset_path = GOLD_DIR / "selic_dataset.csv"
    if not dataset_path.exists():
        raise FileNotFoundError("Gold dataset not found. Run feature build first.")
    df = pd.read_csv(dataset_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).sort_values("date")
    return df


def load_forecast() -> pd.DataFrame:
    forecast_path = ARTIFACTS_DIR / "forecast.csv"
    if not forecast_path.exists():
        raise FileNotFoundError("Forecast not found. Run training pipeline first.")
    df = pd.read_csv(forecast_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["forecast"] = pd.to_numeric(df["forecast"], errors="coerce")
    df = df.dropna(subset=["date", "forecast"]).sort_values("date")
    return df


def build_history_dataset(df: pd.DataFrame) -> pd.DataFrame:
    output = df[["date", "value"]].copy()
    output.rename(columns={"value": "selic_rate"}, inplace=True)
    output["date"] = output["date"].dt.strftime("%Y-%m-%d")
    return output


def build_forecast_dataset(df: pd.DataFrame) -> pd.DataFrame:
    output = df[["date", "forecast"]].copy()
    output.rename(columns={"forecast": "selic_rate_forecast"}, inplace=True)
    output["date"] = output["date"].dt.strftime("%Y-%m-%d")
    output["horizon_days"] = list(range(1, len(output) + 1))
    output["model_version"] = MODEL_VERSION
    return output


def write_metadata(max_horizon: int, output_path: Path) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_source": DATA_SOURCE,
        "model_type": MODEL_TYPE,
        "model_version": MODEL_VERSION,
        "max_forecast_horizon": max_horizon,
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def run() -> None:
    history_df = build_history_dataset(load_gold_dataset())
    forecast_df = build_forecast_dataset(load_forecast())

    history_path = DATASETS_DIR / "selic_history_latest.csv"
    forecast_path = DATASETS_DIR / "selic_forecast_latest.csv"
    metadata_path = DATASETS_DIR / "metadata.json"

    history_df.to_csv(history_path, index=False)
    forecast_df.to_csv(forecast_path, index=False)
    write_metadata(len(forecast_df), metadata_path)

    logger.info("Saved history dataset to %s", history_path)
    logger.info("Saved forecast dataset to %s", forecast_path)
    logger.info("Saved metadata to %s", metadata_path)


if __name__ == "__main__":
    run()
