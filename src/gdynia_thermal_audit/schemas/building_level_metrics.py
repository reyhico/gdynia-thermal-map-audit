"""Building-level metrics schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BuildingLevelMetrics(BaseModel):
    """Per-building thermal metrics record."""

    building_id: str
    unit_id: str | None = Field(default=None, description="Containing spatial unit ID")
    has_anomaly: bool | None = Field(default=None)
    anomaly_scale: int | None = Field(default=None, ge=1, le=5)
    area_m2: float | None = Field(default=None, ge=0, description="Footprint area in m²")
    source: str = Field(description="raster | vector | annotation")
    run_id: str | None = Field(default=None)
