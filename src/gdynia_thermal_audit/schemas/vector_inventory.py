"""Vector inventory record schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class VectorInventoryRecord(BaseModel):
    """Metadata for a downloaded or discovered vector dataset."""

    vector_id: str = Field(description="Unique vector identifier (VEC-NNN)")
    local_path: Optional[str] = Field(default=None)
    source_url: Optional[str] = Field(default=None)
    crs: Optional[str] = Field(default=None)
    feature_count: Optional[int] = Field(default=None)
    geometry_type: Optional[str] = Field(
        default=None,
        description="Geometry type: Point, LineString, Polygon, Multi*, etc.",
    )
    columns: Optional[str] = Field(
        default=None,
        description="Comma-separated list of attribute column names",
    )
    bbox_wgs84: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
