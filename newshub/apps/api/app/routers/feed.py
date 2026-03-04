from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user_id
from app.services.db import get_service_client

router = APIRouter(tags=['feed'])


@router.get('/feed')
def get_feed(
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0, ge=0),
    source_id: str | None = Query(default=None),
    category: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
) -> list[dict]:
    client = get_service_client()
    selected = client.table('user_sources').select('source_id').eq('user_id', user_id).execute().data or []
    source_ids = [row['source_id'] for row in selected]
    if source_id:
        source_ids = [s for s in source_ids if s == source_id]

    if not source_ids:
        return []

    source_select = 'sources!inner(name,category,homepage_url)' if category else 'sources(name,category,homepage_url)'
    query = client.table('articles').select(f'id,title,url,published_at,excerpt,image_url,{source_select}').in_('source_id', source_ids)

    if category:
        query = query.eq('sources.category', category)

    rows = query.order('published_at', desc=True).range(offset, offset + limit - 1).execute().data or []
    return rows
