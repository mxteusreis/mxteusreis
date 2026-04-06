from fastapi import APIRouter, Depends

from app.core.security import verify_internal_token
from app.services.digest import send_daily_digest
from app.services.ingest import ingest_rss_sources

router = APIRouter(prefix='/internal', tags=['internal'])


@router.post('/ingest', dependencies=[Depends(verify_internal_token)])
def ingest() -> dict:
    return ingest_rss_sources()


@router.post('/send-digest', dependencies=[Depends(verify_internal_token)])
def send_digest() -> dict:
    return send_daily_digest()
