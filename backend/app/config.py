"""Application configuration loaded from environment variables with validation."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings with environment variable binding.

    All values can be overridden via environment variables or a `.env` file
    located in the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "MarketIQ"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    API_PREFIX: str = "/api/v1"

    # ── Database (SQLite/PostgreSQL) ─────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./marketiq.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # ── Kafka ────────────────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "marketiq-consumers"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"

    # ── Qdrant ───────────────────────────────────────────────────────────
    QDRANT_HOST: str = ":memory:"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str = "market_articles"
    QDRANT_VECTOR_SIZE: int = 768

    # ── Groq LLM ─────────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.1
    GROQ_MAX_TOKENS: int = 4096

    # ── Embeddings ───────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_BATCH_SIZE: int = 32

    # ── RAG ──────────────────────────────────────────────────────────────
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.65

    # ── Ingestion ────────────────────────────────────────────────────────
    INGESTION_INTERVAL_MINUTES: int = 15
    INGESTION_MAX_ARTICLES_PER_SOURCE: int = 50

    # ── Briefing Schedule ────────────────────────────────────────────────
    MORNING_BRIEFING_HOUR: int = 7
    DAILY_BRIEFING_HOUR: int = 18
    WEEKLY_BRIEFING_DAY: int = 0  # Monday

    # ── Narrative Detection ──────────────────────────────────────────────
    NARRATIVE_DETECTION_INTERVAL_MINUTES: int = 60
    NARRATIVE_MIN_ARTICLES: int = 3
    NARRATIVE_SIMILARITY_THRESHOLD: float = 0.75

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Accept comma-separated string or list for CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def sync_database_url(self) -> str:
        """Return synchronous database URL for Alembic migrations."""
        return self.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
