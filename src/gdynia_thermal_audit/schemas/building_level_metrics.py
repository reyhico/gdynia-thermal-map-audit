"""Building-level metrics schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class BuildingLevelMetrics(BaseModel):
    """Per-building thermal metrics record."""

    building_id: str
    unit_id: Optional[str] = Field(default=None, description="Containing spatial unit ID")
    has_anomaly: Optional[bool] = Field(default=None)
    anomaly_scale: Optional[int] = Field(default=None, ge=1, le=5)
    area_m2: Optional[float] = Field(default=None, ge=0, description="Footprint area in m²")
    source: str = Field(description="raster | vector | annotation")
    run_id: Optional[str] = Field(default=None)
