"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Typed application settings. Required database values are read from .env."""

    app_name: str = Field(validation_alias="APP_NAME")
    app_env: str = Field(validation_alias="APP_ENV")
    debug: bool = Field(validation_alias="DEBUG")

    db_server: str = Field(min_length=1, validation_alias="DB_SERVER")
    db_database: str = Field(min_length=1, validation_alias="DB_DATABASE")
    db_user: str = Field(min_length=1, validation_alias="DB_USER")
    db_password: str = Field(min_length=1, validation_alias="DB_PASSWORD", repr=False)
    db_driver: str = Field(min_length=1, validation_alias="DB_DRIVER")
    db_encrypt: bool = Field(validation_alias="DB_ENCRYPT")
    db_trust_server_certificate: bool = Field(
        validation_alias="DB_TRUST_SERVER_CERTIFICATE"
    )
    db_connection_timeout: PositiveInt = Field(validation_alias="DB_CONNECTION_TIMEOUT")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the application configuration, created once per process."""
    return Settings()
