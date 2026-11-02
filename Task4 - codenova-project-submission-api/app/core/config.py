import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    APP_ENV: str = "development"
    PROJECT_NAME: str = "CodeNova Project Submission API"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./data/submissions.db"

    # JWT Authentication
    JWT_SECRET_KEY: str = "insecure-development-secret-key-change-in-production-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS configuration
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_in_production(cls, v: str, info) -> str:
        env = info.data.get("APP_ENV", "development")
        if env.lower() == "production":
            insecure_defaults = [
                "insecure-development-secret-key-change-in-production-only",
                "replace-with-a-strong-random-secret",
                "replace-with-a-strong-random-secret-for-production",
                "secret",
                "changeme",
            ]
            if v in insecure_defaults or len(v) < 32:
                raise ValueError(
                    "In production environment, JWT_SECRET_KEY must be set to a cryptographically "
                    "secure secret of at least 32 characters."
                )
        return v


settings = Settings()

