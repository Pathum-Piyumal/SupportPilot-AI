from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    app_env: Literal["development", "test"] = "development"
    database_url: str = "postgresql+psycopg://app:local_only@localhost:5432/supportpilot"
    cors_origins: list[str] = ["http://localhost:5173"]
    llm_provider: Literal["fake"] = "fake"


settings = Settings()
