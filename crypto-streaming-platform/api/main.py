from __future__ import annotations

from fastapi import FastAPI

from api.routers.bi import router as bi_router
from api.routers.health import router as health_router
from api.routers.market import router as market_router
from api.settings import settings
from api.storage_repo import StorageRepo

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.on_event("startup")
def startup() -> None:
    app.state.repo = StorageRepo(settings.storage_path)


app.include_router(health_router)
app.include_router(market_router)
app.include_router(bi_router)
