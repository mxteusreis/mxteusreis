from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
import pandas as pd

from api.schema import ForecastResponse, HealthResponse, SelicSeriesResponse
from src.config import ARTIFACTS_DIR, GOLD_DIR

app = FastAPI(title="Selic Forecast API", version="0.1.0")


def load_series() -> pd.DataFrame:
    path = GOLD_DIR / "selic_dataset.csv"
    if not path.exists():
        raise FileNotFoundError("Gold dataset not found. Run feature pipeline first.")
    return pd.read_csv(path)


def load_forecast() -> pd.DataFrame:
    path = ARTIFACTS_DIR / "forecast.csv"
    if not path.exists():
        raise FileNotFoundError("Forecast not found. Run training pipeline first.")
    return pd.read_csv(path)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/series/selic", response_model=SelicSeriesResponse)
def series_selic() -> SelicSeriesResponse:
    try:
        df = load_series()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SelicSeriesResponse(series=df.to_dict(orient="records"))


@app.get("/forecast/selic", response_model=ForecastResponse)
def forecast_selic(horizon: int = Query(30, ge=1, le=365)) -> ForecastResponse:
    try:
        df = load_forecast()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    df = df.head(horizon)
    return ForecastResponse(horizon=horizon, forecasts=df.to_dict(orient="records"))
