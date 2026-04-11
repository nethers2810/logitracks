import json
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LogiTracks API"
    app_version: str = "0.4.0"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://logitracks:logitracks@localhost:5432/logitracks"

    log_level: str = "INFO"
    cors_origins: Annotated[list[str], NoDecode] = ["*"]

    jwt_secret_key: str = "change-me-stage6"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        enable_decoding=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip() for item in value if item and item.strip()]

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []

            if raw.startswith("["):
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
                raise ValueError("CORS_ORIGINS JSON value must be a list")

            return [item.strip() for item in raw.split(",") if item.strip()]

        return []


settings = Settings()
