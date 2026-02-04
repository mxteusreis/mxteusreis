from __future__ import annotations

from typing import List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class SelicSeriesResponse(BaseModel):
    series: List[dict]


class ForecastResponse(BaseModel):
    horizon: int
    forecasts: List[dict]
