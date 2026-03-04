from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user_id
from app.services.db import get_service_client

router = APIRouter(tags=['preferences'])


class SourcePreferencesIn(BaseModel):
    source_ids: list[str]


@router.get('/preferences/sources')
def get_user_sources(user_id: str = Depends(get_current_user_id)) -> list[dict]:
    client = get_service_client()
    rows = (
        client.table('user_sources')
        .select('source_id,sources(id,name,category,homepage_url)')
        .eq('user_id', user_id)
        .execute()
        .data
        or []
    )
    return rows


@router.post('/preferences/sources')
def save_user_sources(payload: SourcePreferencesIn, user_id: str = Depends(get_current_user_id)) -> dict:
    client = get_service_client()
    client.table('user_sources').delete().eq('user_id', user_id).execute()
    to_insert = [{'user_id': user_id, 'source_id': source_id} for source_id in payload.source_ids]
    if to_insert:
        client.table('user_sources').insert(to_insert).execute()
    return {'ok': True, 'selected_sources': len(to_insert)}
