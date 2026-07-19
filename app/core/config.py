from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (.env file).
    Follows 12-factor app methodology.
    """
    APP_NAME: str = "Umbrella Tech"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    DB_SERVER: str = ""
    DB_DATABASE: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
