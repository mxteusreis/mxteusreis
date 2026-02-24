from datetime import datetime
import hashlib

import feedparser
import httpx

from app.services.db import get_service_client


def _hash_article(title: str, url: str) -> str:
    return hashlib.sha256(f'{title.strip()}::{url.strip()}'.encode('utf-8')).hexdigest()


def _build_excerpt(summary: str | None, max_len: int = 220) -> str:
    summary = (summary or '').strip().replace('\n', ' ')
    if len(summary) <= max_len:
        return summary
    return f'{summary[: max_len - 3]}...'


def ingest_rss_sources() -> dict:
    client = get_service_client()
    sources = client.table('sources').select('*').eq('is_active', True).execute().data or []

    inserted = 0
    skipped = 0

    for source in sources:
        feed_resp = httpx.get(source['rss_url'], timeout=15.0)
        parsed = feedparser.parse(feed_resp.text)

        for entry in parsed.entries:
            title = getattr(entry, 'title', '').strip()
            url = getattr(entry, 'link', '').strip()
            if not title or not url:
                skipped += 1
                continue

            article_hash = _hash_article(title, url)
            exists = client.table('articles').select('id').eq('hash', article_hash).limit(1).execute().data
            if exists:
                skipped += 1
                continue

            published_raw = getattr(entry, 'published', None) or getattr(entry, 'updated', None)
            try:
                published_at = datetime.strptime(published_raw, '%a, %d %b %Y %H:%M:%S %z').isoformat() if published_raw else datetime.utcnow().isoformat()
            except ValueError:
                published_at = datetime.utcnow().isoformat()

            summary = getattr(entry, 'summary', None) or getattr(entry, 'description', None)
            media = getattr(entry, 'media_content', None)
            image_url = media[0].get('url') if media and isinstance(media, list) else None

            payload = {
                'source_id': source['id'],
                'title': title,
                'url': url,
                'published_at': published_at,
                'excerpt': _build_excerpt(summary),
                'image_url': image_url,
                'hash': article_hash,
            }
            client.table('articles').insert(payload).execute()
            inserted += 1

    return {'inserted': inserted, 'skipped': skipped, 'sources_processed': len(sources)}
