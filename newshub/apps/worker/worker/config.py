from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    supabase_url: str = Field(alias='SUPABASE_URL')
    supabase_service_role_key: str = Field(alias='SUPABASE_SERVICE_ROLE_KEY')
    resend_api_key: str = Field(alias='RESEND_API_KEY')
    resend_from_email: str = Field(alias='RESEND_FROM_EMAIL')


@lru_cache
def get_settings() -> Settings:
    return Settings()
