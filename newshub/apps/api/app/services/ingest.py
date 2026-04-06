from datetime import datetime
from email.utils import parsedate_to_datetime
import hashlib
import logging
from urllib.parse import urlparse

import feedparser
import httpx

from app.services.db import get_service_client

logger = logging.getLogger(__name__)


def _hash_article(title: str, url: str) -> str:
    return hashlib.sha256(f'{title.strip()}::{url.strip()}'.encode('utf-8')).hexdigest()


def _build_excerpt(summary: str | None, max_len: int = 220) -> str:
    summary = (summary or '').strip().replace('\n', ' ')
    if len(summary) <= max_len:
        return summary
    return f'{summary[: max_len - 3]}...'


def ensure_url_has_scheme(url: str | None) -> str | None:
    if not url:
        return None
    candidate = url.strip()
    parsed = urlparse(candidate)
    if not parsed.scheme:
        candidate = f'https://{candidate}'
        parsed = urlparse(candidate)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        return None
    return candidate


def ingest_rss_sources() -> dict:
    client = get_service_client()
    sources = client.table('sources').select('*').eq('is_active', True).execute().data or []

    inserted = 0
    skipped = 0
    sources_failed = 0
    failures: list[dict[str, str]] = []

    for source in sources:
        source_name = source.get('name', 'Unknown source')
        raw_rss_url = source.get('rss_url')
        rss_url = ensure_url_has_scheme(raw_rss_url)
        if not rss_url:
            error_message = 'Invalid rss_url. Expected http/https URL with netloc.'
            logger.warning('RSS source failed: source=%s rss_url=%s error=%s', source_name, raw_rss_url, error_message)
            sources_failed += 1
            failures.append({'source': source_name, 'rss_url': str(raw_rss_url), 'error': error_message})
            continue

        logger.info('Fetching RSS: %s', rss_url)
        try:
            feed_resp = httpx.get(rss_url, timeout=15.0, follow_redirects=True)
            feed_resp.raise_for_status()
            parsed = feedparser.parse(feed_resp.text)
        except httpx.ConnectError as exc:
            logger.warning('RSS source failed: source=%s rss_url=%s error=%s', source_name, rss_url, str(exc))
            sources_failed += 1
            failures.append({'source': source_name, 'rss_url': rss_url, 'error': f'ConnectError: {exc}'})
            continue
        except httpx.TimeoutException as exc:
            logger.warning('RSS source failed: source=%s rss_url=%s error=%s', source_name, rss_url, str(exc))
            sources_failed += 1
            failures.append({'source': source_name, 'rss_url': rss_url, 'error': f'TimeoutException: {exc}'})
            continue
        except httpx.RequestError as exc:
            logger.warning('RSS source failed: source=%s rss_url=%s error=%s', source_name, rss_url, str(exc))
            sources_failed += 1
            failures.append({'source': source_name, 'rss_url': rss_url, 'error': f'RequestError: {exc}'})
            continue
        except Exception as exc:
            logger.exception('RSS source failed unexpectedly: source=%s rss_url=%s', source_name, rss_url)
            sources_failed += 1
            failures.append({'source': source_name, 'rss_url': rss_url, 'error': f'UnexpectedError: {exc}'})
            continue

        for entry in parsed.entries:
            title = getattr(entry, 'title', '').strip()
            url = getattr(entry, 'link', '').strip()
            if not title or not url:
                skipped += 1
                continue

            article_hash = _hash_article(title, url)
            exists = client.table('articles').select('id').eq('hash', article_hash).limit(1).execute().data
            if exists:
                logger.info('Skipping duplicate article by hash: %s', url)
                skipped += 1
                continue

            exists_url = client.table('articles').select('id').eq('url', url).limit(1).execute().data
            if exists_url:
                logger.info('Skipping duplicate article by url: %s', url)
                skipped += 1
                continue

            published_raw = getattr(entry, 'published', None) or getattr(entry, 'updated', None)
            try:
                published_at = parsedate_to_datetime(published_raw).isoformat() if published_raw else datetime.utcnow().isoformat()
            except (TypeError, ValueError):
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
            try:
                client.table('articles').insert(payload).execute()
                logger.info('Inserted new article: %s', url)
                inserted += 1
            except Exception as exc:
                message = str(exc).lower()
                if 'duplicate key' in message or 'articles_url_key' in message:
                    logger.info('Skipping duplicate article after insert conflict: %s', url)
                    skipped += 1
                    continue
                raise

    summary = {
        'inserted': inserted,
        'skipped': skipped,
        'sources_processed': len(sources),
        'sources_failed': sources_failed,
        'failures': failures,
    }
    logger.info('Ingest summary: %s', summary)
    return summary
