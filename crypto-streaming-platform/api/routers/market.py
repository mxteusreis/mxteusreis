from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from api.deps import get_repo
from api.settings import settings
from api.storage_repo import StorageRepo

router = APIRouter(tags=["market"])


@router.get("/symbols")
def symbols() -> dict:
    return {"symbols": settings.symbols}


@router.get("/trades/latest")
def trades_latest(
    symbol: str = Query(...),
    limit: int = Query(200, ge=1, le=5000),
    repo: StorageRepo = Depends(get_repo),
) -> dict:
    return {"items": repo.query_latest(symbol=symbol, limit=limit)}


@router.get("/trades/range")
def trades_range(
    symbol: str,
    start: datetime,
    end: datetime,
    repo: StorageRepo = Depends(get_repo),
) -> dict:
    return {"items": repo.query_range(symbol=symbol, start=start, end=end)}
