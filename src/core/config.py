"""
Application configuration using pydantic-settings.

Loads environment variables from .env file and provides validated settings
for the Photo to Marketplace Search application.
"""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    claude_model: str = Field(default="claude-sonnet-4-20250514")

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=10)
    allowed_extensions: set[str] = Field(default={".jpg", ".jpeg", ".png", ".webp"})
    upload_dir: str = Field(default="uploads")

    # API Limits
    vision_api_timeout: int = Field(default=30)
    max_concurrent_uploads: int = Field(default=10)

    # Link Validation Configuration
    link_validation_enabled: bool = Field(default=True)
    link_validation_timeout: int = Field(default=3)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance with all configuration loaded.

    Raises:
        ValidationError: If required environment variables are missing.
    """
    return Settings()  # type: ignore[call-arg]
