from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MiniWorld Agent"
    FRONTEND_HOST: str = "http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./miniworld.db"
    FASTAPI_ENV: Literal["development", "test", "production"] = "development"
    EXECUTION_MODE: Literal["demo", "live"] = "demo"
    SEED_DEMO_DATA: bool = True

    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_BYTES: int = 8 * 1024 * 1024

    MODEL_PROVIDER_MODE: Literal["demo", "openai", "disabled"] = "demo"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-5.6"

    ALLOW_LIVE_JOB_SEARCH: bool = False
    JOB_RESULTS_LIMIT: int = 12
    JOB_SCHEDULE_MINUTES: int = 720
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_POLL_SECONDS: int = Field(default=60, ge=1, le=3600)

    LANGGRAPH_CHECKPOINT_MODE: Literal["memory", "postgres"] = "memory"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> str:
        database_url = str(value)
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+psycopg://", 1)
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return database_url

    @property
    def checkpoint_database_url(self) -> str:
        return self.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
