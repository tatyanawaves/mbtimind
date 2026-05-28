"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # App
    APP_NAME: str = "MBTI Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./mbti_platform.db"

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # Test Engine
    QUESTIONS_PER_TEST: int = 60
    MIN_ANSWER_TIME_MS: int = 800  # Anti-cheating: min time per question
    MAX_ANSWER_TIME_MS: int = 60000  # 60 seconds max
    L_SCALE_THRESHOLD: int = 4  # Max L-scale violations before flagging

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
