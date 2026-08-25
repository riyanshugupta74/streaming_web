"""Peblo TV Mini - Application configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://peblo:peblo@db:5432/peblo"
    database_url_sync: str = "postgresql://peblo:peblo@db:5432/peblo"

    # JWT
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480  # 8 hours

    # Storage
    storage_type: str = "local"
    storage_path: str = "/app/storage"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:3001,http://localhost:3002"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
