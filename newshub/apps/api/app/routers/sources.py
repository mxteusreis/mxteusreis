from fastapi import APIRouter

from app.services.db import get_anon_client

router = APIRouter(tags=['sources'])


@router.get('/sources')
def list_sources() -> list[dict]:
    client = get_anon_client()
    rows = client.table('sources').select('*').eq('is_active', True).order('name').execute().data or []
    return rows
