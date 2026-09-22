from typing import List, Union
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables or .env file.
    """
    APP_NAME: str = "AgriPulse"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security & Auth settings
    JWT_SECRET_KEY: str = Field("development_secret_key_change_in_production_98234", alias="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # PostgreSQL Database URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/agripulse_db"

    # External APIs
    WEATHER_API_KEY: str = ""

    # CORS Whitelist
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:4200"

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
        case_sensitive=True
    )


settings = Settings()
