from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    api_title: str = Field(default='newshub-api', alias='API_TITLE')
    supabase_url: str = Field(alias='SUPABASE_URL')
    supabase_anon_key: str = Field(alias='SUPABASE_ANON_KEY')
    supabase_service_role_key: str = Field(alias='SUPABASE_SERVICE_ROLE_KEY')
    supabase_jwt_secret: str = Field(alias='SUPABASE_JWT_SECRET')
    internal_token: str = Field(alias='INTERNAL_TOKEN')
    resend_api_key: str = Field(alias='RESEND_API_KEY')
    resend_from_email: str = Field(alias='RESEND_FROM_EMAIL')
    web_base_url: str = Field(default='http://localhost:3000', alias='WEB_BASE_URL')


@lru_cache
def get_settings() -> Settings:
    return Settings()
