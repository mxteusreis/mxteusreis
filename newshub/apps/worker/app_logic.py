from datetime import datetime
import hashlib
from zoneinfo import ZoneInfo

import feedparser
import httpx
import resend

from worker.config import get_settings
from worker.db import get_client


def ingest():
    client = get_client()
    sources = client.table('sources').select('*').eq('is_active', True).execute().data or []
    inserted = 0

    for source in sources:
        feed_resp = httpx.get(source['rss_url'], timeout=15.0)
        parsed = feedparser.parse(feed_resp.text)

        for entry in parsed.entries:
            title = getattr(entry, 'title', '').strip()
            url = getattr(entry, 'link', '').strip()
            if not title or not url:
                continue

            hash_value = hashlib.sha256(f'{title}::{url}'.encode()).hexdigest()
            exists = client.table('articles').select('id').eq('hash', hash_value).limit(1).execute().data
            if exists:
                continue

            summary = (getattr(entry, 'summary', '') or '').strip().replace('\n', ' ')
            excerpt = f"{summary[:217]}..." if len(summary) > 220 else summary
            published_at = datetime.utcnow().isoformat()

            client.table('articles').insert(
                {
                    'source_id': source['id'],
                    'title': title,
                    'url': url,
                    'published_at': published_at,
                    'excerpt': excerpt,
                    'image_url': None,
                    'hash': hash_value,
                }
            ).execute()
            inserted += 1

    return {'sources': len(sources), 'inserted': inserted}


def send_digest():
    settings = get_settings()
    resend.api_key = settings.resend_api_key
    client = get_client()

    today = datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()
    users = client.table('user_sources').select('user_id').execute().data or []
    user_ids = sorted({u['user_id'] for u in users})

    sent = 0
    for user_id in user_ids:
        source_ids = [row['source_id'] for row in client.table('user_sources').select('source_id').eq('user_id', user_id).execute().data or []]
        if not source_ids:
            continue

        articles = (
            client.table('articles')
            .select('title,url,excerpt,published_at,sources(name)')
            .in_('source_id', source_ids)
            .gte('published_at', f'{today}T00:00:00')
            .lte('published_at', f'{today}T23:59:59')
            .order('published_at', desc=True)
            .limit(10)
            .execute()
            .data
            or []
        )
        if not articles:
            continue

        user_data = client.auth.admin.get_user_by_id(user_id)
        email = user_data.user.email if user_data and user_data.user else None
        if not email:
            continue

        items = ''.join([f"<li><a href='{a['url']}'>{a['title']}</a><p>{a['excerpt']}</p></li>" for a in articles])
        resend.Emails.send(
            {
                'from': settings.resend_from_email,
                'to': [email],
                'subject': f'Newshub Digest - {today}',
                'html': f'<h2>Seu digest diário</h2><ul>{items}</ul>',
            }
        )

        client.table('digests').insert({'user_id': user_id, 'digest_date': today, 'sent_at': datetime.utcnow().isoformat(), 'status': 'sent'}).execute()
        sent += 1

    return {'users': len(user_ids), 'sent': sent}
