"""Spatial unit metrics schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SpatialUnitMetrics(BaseModel):
    """All indicator fields for one spatial unit in one pipeline run."""

    unit_id: str
    unit_type: str = Field(description="district | neighborhood | grid")
    geometry_wkt: Optional[str] = Field(default=None)
    data_source: str = Field(description="raster | vector | annotation")
    run_id: Optional[str] = Field(default=None)

    # Raster indicators (Scenario A)
    coverage_ratio: Optional[float] = Field(default=None, ge=0, le=1)
    mean_intensity: Optional[float] = Field(default=None)
    median_intensity: Optional[float] = Field(default=None)
    anomalous_area_share: Optional[float] = Field(default=None, ge=0, le=1)

    # Vector/Annotation indicators (Scenarios B & C)
    anomaly_count: Optional[int] = Field(default=None, ge=0)
    anomaly_density_per_ha: Optional[float] = Field(default=None, ge=0)
    building_anomaly_count: Optional[int] = Field(default=None, ge=0)
    building_anomaly_share: Optional[float] = Field(default=None, ge=0, le=1)

    # Composite
    priority_index: Optional[float] = Field(default=None)
