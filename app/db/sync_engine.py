from sqlalchemy import create_engine

from app.config import get_settings

_settings = get_settings()
sync_engine = create_engine(_settings.sync_database_url, pool_pre_ping=True)
