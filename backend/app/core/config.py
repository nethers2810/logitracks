import json
from typing import Annotated, Any

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
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []

            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError("CORS_ORIGINS JSON value must be a valid JSON array") from exc

                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON value must be a list")

                return [str(item).strip() for item in parsed if str(item).strip()]

            return [item.strip() for item in raw.split(",") if item.strip()]

        raise ValueError("CORS_ORIGINS must be a list or string")


settings = Settings()
