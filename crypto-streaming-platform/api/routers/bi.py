from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query, Response

from api.deps import get_repo
from api.storage_repo import StorageRepo

router = APIRouter(prefix="/bi", tags=["bi"])


def _to_csv(rows: list[dict], headers: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


@router.get("/daily_ohlc.csv")
def daily_ohlc_csv(
    symbol: str = Query(...),
    days: int = Query(90, ge=1, le=3650),
    repo: StorageRepo = Depends(get_repo),
) -> Response:
    rows = repo.bi_daily_ohlc(symbol=symbol, days=days)
    content = _to_csv(rows, ["date", "open", "high", "low", "close"])
    return Response(content=content, media_type="text/csv", headers={"Cache-Control": "public, max-age=60"})


@router.get("/daily_volume.csv")
def daily_volume_csv(
    symbol: str = Query(...),
    days: int = Query(90, ge=1, le=3650),
    repo: StorageRepo = Depends(get_repo),
) -> Response:
    rows = repo.bi_daily_volume(symbol=symbol, days=days)
    content = _to_csv(rows, ["date", "volume"])
    return Response(content=content, media_type="text/csv", headers={"Cache-Control": "public, max-age=60"})


@router.get("/latest_prices.csv")
def latest_prices_csv(
    symbols: str = Query(...),
    repo: StorageRepo = Depends(get_repo),
) -> Response:
    rows = []
    for symbol in [item.strip().upper() for item in symbols.split(",") if item.strip()]:
        latest = repo.query_latest(symbol=symbol, limit=1)
        if latest:
            event = latest[0]
            rows.append(
                {
                    "symbol": event["symbol"],
                    "timestamp_utc": event["timestamp_utc"],
                    "lastPrice": event["lastPrice"],
                    "priceChangePercent": event["priceChangePercent"],
                    "volume": event["volume"],
                }
            )

    content = _to_csv(rows, ["symbol", "timestamp_utc", "lastPrice", "priceChangePercent", "volume"])
    return Response(content=content, media_type="text/csv", headers={"Cache-Control": "public, max-age=30"})
