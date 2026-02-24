from datetime import datetime
from zoneinfo import ZoneInfo

import resend

from app.core.config import get_settings
from app.services.db import get_service_client


def _render_digest_html(user_email: str, articles: list[dict], digest_date: str) -> str:
    rows = ''.join(
        f"<li><a href='{a['url']}'>{a['title']}</a><br/><small>{a['source_name']} - {a['published_at']}</small><p>{a['excerpt']}</p></li>"
        for a in articles
    )
    return f"<h2>Seu digest - {digest_date}</h2><p>Olá, {user_email}!</p><ul>{rows}</ul><p>Leia os artigos completos nos links originais.</p>"


def send_daily_digest() -> dict:
    settings = get_settings()
    resend.api_key = settings.resend_api_key
    client = get_service_client()

    tz = ZoneInfo('America/Sao_Paulo')
    today = datetime.now(tz).date().isoformat()

    users = client.table('user_sources').select('user_id').execute().data or []
    user_ids = sorted({u['user_id'] for u in users})
    sent = 0

    for user_id in user_ids:
        source_rows = client.table('user_sources').select('source_id').eq('user_id', user_id).execute().data or []
        source_ids = [row['source_id'] for row in source_rows]
        if not source_ids:
            continue

        articles = (
            client.table('articles')
            .select('title,url,published_at,excerpt,sources(name)')
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

        normalized = [
            {
                'title': a['title'],
                'url': a['url'],
                'published_at': a['published_at'],
                'excerpt': a['excerpt'],
                'source_name': a['sources']['name'] if a.get('sources') else 'Fonte',
            }
            for a in articles
        ]

        resend.Emails.send(
            {
                'from': settings.resend_from_email,
                'to': [email],
                'subject': f'Newshub Digest - {today}',
                'html': _render_digest_html(email, normalized, today),
            }
        )

        client.table('digests').insert(
            {
                'user_id': user_id,
                'digest_date': today,
                'sent_at': datetime.utcnow().isoformat(),
                'status': 'sent',
            }
        ).execute()
        sent += 1

    return {'users_processed': len(user_ids), 'digests_sent': sent}
