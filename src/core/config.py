"""
Application configuration.
"""
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load variables from .env before the Settings class is instantiated
# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Receipt Processing API"
    VERSION: str = "1.0.0"

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", min_length=1, description="OpenAI API key is required")
    DEFAULT_EXTRACTION_MODEL: str = "gpt-4o-mini"
    DEFAULT_AUDIT_MODEL: str = "gpt-4o-mini"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # Pydantic-settings config
    model_config = SettingsConfigDict(env_file=str(env_path), case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()