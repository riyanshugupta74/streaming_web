"""Peblo TV Mini - Application configuration."""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


def _get_database_url() -> str:
    """Get async database URL, converting from Render's format if needed."""
    url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://peblo:peblo@db:5432/peblo").strip()
    # Render provides postgres:// or postgresql:// but asyncpg needs postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Fallback to catch anything else if it doesn't have the driver
    if url.startswith("postgresql") and not url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql", "postgresql+asyncpg", 1)
        
    return url


def _get_sync_database_url() -> str:
    """Get sync database URL, converting from Render's format if needed."""
    url = os.environ.get(
        "DATABASE_URL_SYNC",
        os.environ.get("DATABASE_URL", "postgresql://peblo:peblo@db:5432/peblo")
    ).strip()
    
    # Ensure it starts with postgresql:// (not postgres:// or postgresql+asyncpg://)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        
    return url


from pydantic import Field, field_validator

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(default_factory=_get_database_url)
    database_url_sync: str = Field(default_factory=_get_sync_database_url)

    @field_validator("database_url", mode="before")
    @classmethod
    def parse_database_url(cls, v: str) -> str:
        if not v:
            return v
        v = v.strip()
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql+psycopg2://"):
            v = v.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        
        if v.startswith("postgresql") and not v.startswith("postgresql+asyncpg"):
            v = v.replace("postgresql", "postgresql+asyncpg", 1)
        return v

    @field_validator("database_url_sync", mode="before")
    @classmethod
    def parse_database_url_sync(cls, v: str) -> str:
        if not v:
            return v
        v = v.strip()
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        elif v.startswith("postgresql+asyncpg://"):
            v = v.replace("postgresql+asyncpg://", "postgresql://", 1)
        return v

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
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:3001,http://localhost:3002,https://streaming-web-veiwer.onrender.com,https://streaming-web-cms.onrender.com"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
