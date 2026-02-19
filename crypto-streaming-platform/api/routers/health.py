from __future__ import annotations

from fastapi import APIRouter, Depends

from api.deps import get_repo
from api.schemas import HealthResponse
from api.settings import settings
from api.storage_repo import StorageRepo

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(repo: StorageRepo = Depends(get_repo)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        last_ingest_time=repo.last_ingest_time(),
    )
