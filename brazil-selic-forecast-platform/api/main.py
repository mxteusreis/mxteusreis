from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Response
import pandas as pd

from api.schema import ForecastResponse, HealthResponse, SelicSeriesResponse
from src.config import ARTIFACTS_DIR, DATASETS_DIR, GOLD_DIR

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


def read_dataset_csv(filename: str) -> str:
    path = DATASETS_DIR / filename
    if not path.exists():
        raise FileNotFoundError("Dataset not found. Run export pipeline first.")
    return path.read_text(encoding="utf-8")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/series/selic", response_model=SelicSeriesResponse)
def series_selic(
    start: str | None = Query(None, description="Start date YYYY-MM-DD"),
    end: str | None = Query(None, description="End date YYYY-MM-DD"),
) -> SelicSeriesResponse:
    try:
        df = load_series()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    date_series = pd.to_datetime(df["date"], errors="coerce")
    valid_mask = date_series.notna()
    df = df[valid_mask]
    date_series = date_series[valid_mask]
    if start:
        start_dt = pd.to_datetime(start, errors="coerce")
        if pd.notna(start_dt):
            df = df[date_series >= start_dt]
    if end:
        end_dt = pd.to_datetime(end, errors="coerce")
        if pd.notna(end_dt):
            df = df[date_series <= end_dt]
    return SelicSeriesResponse(series=df.to_dict(orient="records"))


@app.get("/forecast/selic", response_model=ForecastResponse)
def forecast_selic(horizon: int = Query(30, ge=1, le=365)) -> ForecastResponse:
    try:
        df = load_forecast()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    df = df.head(horizon)
    return ForecastResponse(horizon=horizon, forecasts=df.to_dict(orient="records"))


@app.get("/bi/selic/history")
def bi_selic_history() -> Response:
    try:
        csv_data = read_dataset_csv("selic_history_latest.csv")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(content=csv_data, media_type="text/csv")


@app.get("/bi/selic/forecast")
def bi_selic_forecast() -> Response:
    try:
        csv_data = read_dataset_csv("selic_forecast_latest.csv")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(content=csv_data, media_type="text/csv")


@app.get("/bi/metadata")
def bi_metadata() -> Response:
    try:
        metadata = read_dataset_csv("metadata.json")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(content=metadata, media_type="application/json")
