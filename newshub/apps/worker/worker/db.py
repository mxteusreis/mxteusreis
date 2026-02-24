from supabase import create_client

from worker.config import get_settings


def get_client():
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
