from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: Literal["development", "testing", "production"] = "development"
    project_name: str = "Sponsorship CRM"
    api_v1_prefix: str = "/api/v1"

    db_scheme: str = "sqlite+aiosqlite"
    db_user: str | None = None
    db_password: str | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_name: str = "./sponsorship_crm.db"

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:4173",
        ]
    )

    log_level: str = "INFO"
    scheduler_timezone: str = "UTC"

    @property
    def database_url(self) -> str:
        if self.db_scheme.startswith("sqlite"):
            return f"{self.db_scheme}:///{self.db_name}"

        credentials = ""
        if self.db_user and self.db_password:
            credentials = f"{self.db_user}:{self.db_password}@"

        port = f":{self.db_port}" if self.db_port else ""
        return f"{self.db_scheme}://{credentials}{self.db_host or 'localhost'}{port}/{self.db_name}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
