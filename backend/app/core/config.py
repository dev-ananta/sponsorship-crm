import logging
from typing import Literal
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    PROJECT_NAME: str = "Sponsorship CRM"
    API_V1_STR: str = "/api/v1"

    # Database Configuration
    DB_SCHEME: str = "sqlite+aiosqlite"
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: str | None = None
    DB_PATH: str = "./sponsorship_crm.db"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Dynamically computes connection string based on driver choice."""
        if "sqlite" in self.DB_SCHEME:
            return f"{self.DB_SCHEME}:///{self.DB_PATH}"
        return f"{self.DB_SCHEME}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_PATH}"

    # Application Configuration
    LOG_LEVEL: int = logging.INFO
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
