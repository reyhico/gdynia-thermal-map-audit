"""Annotation record Pydantic schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from gdynia_thermal_audit.constants import (
    ANOMALY_SCALE_MAX,
    ANOMALY_SCALE_MIN,
    VISIBILITY_QUALITY_MAX,
    VISIBILITY_QUALITY_MIN,
)


class AnnotationRecord(BaseModel):
    """One manual annotation observation record."""

    record_id: str = Field(description="Unique identifier, format ANN-YYYYMMDD-NNNN")
    building_id: Optional[str] = Field(default=None)
    lon: float = Field(ge=-180, le=180, description="WGS-84 longitude")
    lat: float = Field(ge=-90, le=90, description="WGS-84 latitude")
    address: Optional[str] = Field(default=None)
    district: Optional[str] = Field(default=None)
    neighborhood: Optional[str] = Field(default=None)
    spatial_unit_id: Optional[str] = Field(default=None)
    source_url: str = Field(description="Viewer URL at time of observation")
    screenshot_ref: Optional[str] = Field(default=None)
    observed_anomaly: bool = Field(description="True if thermal anomaly observed")
    anomaly_scale_1_5: Optional[int] = Field(
        default=None,
        ge=ANOMALY_SCALE_MIN,
        le=ANOMALY_SCALE_MAX,
        description="Visual intensity 1 (faint) to 5 (intense)",
    )
    apparent_area_m2: Optional[float] = Field(default=None, ge=0)
    roof_flag: Optional[bool] = Field(default=None)
    facade_flag: Optional[bool] = Field(default=None)
    network_adjacent_flag: Optional[bool] = Field(default=None)
    visibility_quality: int = Field(
        ge=VISIBILITY_QUALITY_MIN,
        le=VISIBILITY_QUALITY_MAX,
        description="1 = clear, 2 = partial, 3 = poor",
    )
    annotator: str = Field(description="Annotator initials or identifier")
    annotation_date: str = Field(description="ISO 8601 date (YYYY-MM-DD)")
    notes: Optional[str] = Field(default=None)

    @field_validator("annotation_date")
    @classmethod
    def _validate_date_format(cls, v: str) -> str:
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError(f"annotation_date must be YYYY-MM-DD, got '{v}'")
        return v

    @field_validator("anomaly_scale_1_5")
    @classmethod
    def _scale_only_if_anomaly(cls, v: Optional[int]) -> Optional[int]:
        return v
