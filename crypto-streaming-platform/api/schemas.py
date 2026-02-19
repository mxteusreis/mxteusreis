from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    last_ingest_time: str | None


class TradeEvent(BaseModel):
    timestamp_utc: datetime
    symbol: str
    lastPrice: float
    priceChangePercent: float
    volume: float
    source: str
