from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LogiTracks API"
    app_version: str = "0.4.0"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://logitracks:logitracks@localhost:5432/logitracks"

    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]

    jwt_secret_key: str = "change-me-stage6"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


settings = Settings()
