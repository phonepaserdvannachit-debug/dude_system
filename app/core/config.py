from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # ---------------- APP ----------------
    APP_NAME: str = "Dude Payment Sharing System"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ---------------- SECURITY ----------------
    SECRET_KEY: str = Field(default="change-this-before-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    REMEMBER_USERNAME_DAYS: int = 5

    # ---------------- DATABASE ----------------
    DATABASE_URL: str = "mysql+pymysql://root:2580@127.0.0.1:3306/dude_system"

    # ---------------- CORS ----------------
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # ---------------- SUPABASE ----------------
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    SUPABASE_BUCKET_PROFILES: str = "person-profiles"
    SUPABASE_BUCKET_QR: str = "person-qr"
    SUPABASE_BUCKET_SLIPS: str = "payment-slip"

    # ---------------- VALIDATOR ----------------
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
    


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
