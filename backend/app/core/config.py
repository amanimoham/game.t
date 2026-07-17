"""Application configuration.

All settings load from environment variables (or a local ``.env`` file).
The database/redis URLs are computed so that either discrete parts
(POSTGRES_HOST, ...) or a single injected URL (DATABASE_URL on Render) work.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "Muharabat Al-Mughriyat API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ---- Security (consumed from Step 3) ----
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ALGORITHM: str = "HS256"

    # ---- PostgreSQL ----
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app"
    POSTGRES_DB: str = "savings_game"
    # Optional full override (Render injects DATABASE_URL directly).
    DATABASE_URL: str | None = None

    # ---- Redis ----
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str | None = None

    # ---- CORS ----
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        # Accept a comma-separated string from env, e.g. "https://a.com,https://b.com".
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy URL (asyncpg driver)."""
        if self.DATABASE_URL:
            return self._normalize_async(self.DATABASE_URL)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @staticmethod
    def _normalize_async(url: str) -> str:
        # Managed providers hand out "postgres://" / "postgresql://";
        # coerce to the asyncpg driver SQLAlchemy expects.
        if url.startswith("postgresql+asyncpg://"):
            return url
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
