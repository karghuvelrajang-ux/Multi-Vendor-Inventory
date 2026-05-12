from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Multi-Vendor Inventory Sync Engine"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/inventory_sync"
    )
    sync_database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/inventory_sync"
    )

    jwt_secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "rpc://"

    oauth_google_client_id: str = ""
    oauth_google_client_secret: str = ""
    oauth_redirect_base_url: str = "http://localhost:8000"

    webhook_hmac_secret: str = "webhook-hmac-secret-change-in-production"

    session_secret_key: str = "session-secret-change-me"


@lru_cache
def get_settings() -> Settings:
    return Settings()
