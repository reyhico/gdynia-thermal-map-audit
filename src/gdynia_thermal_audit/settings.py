"""Application settings loaded from environment variables / .env file."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from gdynia_thermal_audit.constants import (
    DEFAULT_REQUEST_DELAY_S,
    DEFAULT_USER_AGENT,
    TARGET_LANDING_URL,
)


class Settings(BaseSettings):
    """All runtime configuration, resolved from environment or .env file."""

    model_config = SettingsConfigDict(
        env_prefix="GTA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Paths
    data_dir: Path = Field(default=Path("data"), description="Root data directory")
    output_dir: Path = Field(default=Path("outputs"), description="Root output directory")

    # Logging
    log_level: str = Field(default="INFO", description="Python logging level")

    # Network
    request_delay_s: float = Field(
        default=DEFAULT_REQUEST_DELAY_S,
        ge=0.0,
        description="Minimum delay (seconds) between HTTP requests",
    )
    max_retries: int = Field(default=3, ge=0, description="Maximum HTTP retry count")
    user_agent: str = Field(
        default=DEFAULT_USER_AGENT,
        description="HTTP User-Agent header sent with all requests",
    )

    # Target URLs
    target_url: str = Field(
        default=TARGET_LANDING_URL,
        description="Landing page URL of the target thermal platform",
    )
    viewer_url: str = Field(
        default=TARGET_LANDING_URL,
        description="Viewer URL (may differ from landing page)",
    )

    # Config file
    config_path: Path = Field(
        default=Path("config/config.example.yaml"),
        description="Path to the project YAML config file",
    )

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got '{v}'")
        return upper
