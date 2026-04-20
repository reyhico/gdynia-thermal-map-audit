"""Pipeline run log schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PipelineRunLog(BaseModel):
    """Provenance record for a single pipeline invocation."""

    run_id: str = Field(description="UUID v4 identifying this run")
    start_time: str = Field(description="UTC ISO 8601 start timestamp")
    end_time: str | None = Field(default=None, description="UTC ISO 8601 end timestamp")
    scenario: str = Field(
        description="Scenario used: auto | raster | vector | annotation",
        default="auto",
    )
    steps_completed: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    output_paths: dict[str, str] = Field(default_factory=dict)
    config_hash: str | None = Field(
        default=None, description="SHA-256 of the active config YAML file"
    )
    python_version: str | None = Field(default=None)
    package_version: str | None = Field(default=None)
