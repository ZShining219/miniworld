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
    RADAR_MAP_DIR: Path = Path("runtime-data/maps")

    MODEL_PROVIDER_MODE: Literal["demo", "openai", "disabled"] = "demo"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-5.6"

    # Fitness Coach has its own provider selection so it cannot silently
    # inherit the career/work reporting model configuration.
    FITNESS_AGENT_PROVIDER: Literal["deepseek", "demo", "disabled"] = "deepseek"
    FITNESS_AGENT_API_KEY: str | None = None
    FITNESS_AGENT_MODEL: str = "deepseek-chat"
    FITNESS_AGENT_BASE_URL: str = "https://api.deepseek.com"
    FITNESS_AGENT_TIMEOUT_SECONDS: float = Field(default=30, ge=1, le=120)

    ALLOW_LIVE_JOB_SEARCH: bool = False
    LIVE_JOB_SOURCE: Literal["lever", "jobspy", "greenhouse"] = "lever"
    LEVER_SITES: str = "binance"
    LEVER_TIMEOUT_SECONDS: float = Field(default=15, ge=1, le=60)
    GREENHOUSE_BOARDS: str = ""
    GREENHOUSE_TIMEOUT_SECONDS: float = Field(default=15, ge=1, le=60)
    JOB_RESULTS_LIMIT: int = 12
    JOB_SCHEDULE_MINUTES: int = 720
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_POLL_SECONDS: int = Field(default=60, ge=1, le=3600)
    RADAR_FETCH_SOURCES: str = "demo"
    RADAR_SCENE_MAX_JOBS: int = Field(default=400, ge=1, le=2000)

    # The job radar enrichment provider is an independent opt-in channel so it
    # cannot silently inherit career/work reporting model settings.
    JOB_AGENT_PROVIDER: Literal["deepseek", "demo", "disabled"] = "demo"
    JOB_AGENT_API_KEY: str | None = None
    JOB_AGENT_MODEL: str = "deepseek-chat"
    JOB_AGENT_BASE_URL: str = "https://api.deepseek.com"
    JOB_AGENT_TIMEOUT_SECONDS: float = Field(default=30, ge=1, le=120)
    JOB_LLM_MAX_PER_RUN: int = Field(default=8, ge=0, le=50)

    # Optional read/push bridge to the local interview practice project.
    INTERVIEW_AGENT_BASE_URL: str = "http://127.0.0.1:8788"
    INTERVIEW_AGENT_DIR: str | None = None
    INTERVIEW_AGENT_KEY_FILE: str | None = None
    INTERVIEW_AGENT_TIMEOUT_SECONDS: float = Field(default=10, ge=1, le=60)
    INTERVIEW_HANDOFF_DIR: Path = Path("runtime-data/interview-handoff")

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

    @property
    def lever_sites(self) -> tuple[str, ...]:
        return tuple(site.strip() for site in self.LEVER_SITES.split(",") if site.strip())

    @property
    def greenhouse_boards(self) -> tuple[str, ...]:
        return tuple(
            board.strip()
            for board in self.GREENHOUSE_BOARDS.split(",")
            if board.strip()
        )

    @property
    def radar_fetch_sources(self) -> tuple[str, ...]:
        seen: list[str] = []
        for name in self.RADAR_FETCH_SOURCES.split(","):
            cleaned = name.strip().lower()
            if cleaned and cleaned not in seen:
                seen.append(cleaned)
        return tuple(seen)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
