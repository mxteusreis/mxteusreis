from supabase import Client, create_client

from app.core.config import Settings, get_settings


def get_anon_client(settings: Settings | None = None) -> Client:
    settings = settings or get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_service_client(settings: Settings | None = None) -> Client:
    settings = settings or get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
