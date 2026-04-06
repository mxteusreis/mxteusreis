from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import feed, health, internal, preferences, sources

settings = get_settings()
app = FastAPI(title=settings.api_title)

app.include_router(health.router)
app.include_router(sources.router)
app.include_router(preferences.router)
app.include_router(feed.router)
app.include_router(internal.router)
