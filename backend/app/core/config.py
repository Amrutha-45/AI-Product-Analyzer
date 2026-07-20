"""
core/config.py
--------------
Centralised settings loaded from environment variables (or .env file).
All other modules import from here — never from os.environ directly.
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────
    app_env: str = "development"
    app_version: str = "1.0.0"
    frontend_origin: str = "http://localhost:5173"

    # ── AI Provider ───────────────────────────
    ai_provider: str = Field(default="groq", description="AI Provider (gemini or groq)")
    ai_model: str = Field(default="llama-3.2-90b-vision-preview", description="Model name to use")
    ai_temperature: float = Field(default=0.0, description="Temperature for generation")
    ai_timeout_seconds: int = Field(default=30, description="Timeout for AI calls")
    gemini_api_key: str | None = Field(default=None)
    groq_api_key: str | None = Field(default=None)

    # ── Supabase ──────────────────────────────
    supabase_url: str = ""
    supabase_service_key: str = ""

    # ── Rate Limiting ─────────────────────────
    rate_limit_scans_per_hour: int = 10

    # ── Image Validation ──────────────────────
    max_image_size_mb: int = 8
    min_image_dimension: int = 200

    @property
    def max_image_size_bytes(self) -> int:
        return self.max_image_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance. Use this everywhere."""
    return Settings()
