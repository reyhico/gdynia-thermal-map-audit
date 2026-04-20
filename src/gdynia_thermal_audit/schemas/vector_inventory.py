"""Vector inventory record schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VectorInventoryRecord(BaseModel):
    """Metadata for a downloaded or discovered vector dataset."""

    vector_id: str = Field(description="Unique vector identifier (VEC-NNN)")
    local_path: str | None = Field(default=None)
    source_url: str | None = Field(default=None)
    crs: str | None = Field(default=None)
    feature_count: int | None = Field(default=None)
    geometry_type: str | None = Field(
        default=None,
        description="Geometry type: Point, LineString, Polygon, Multi*, etc.",
    )
    columns: str | None = Field(
        default=None,
        description="Comma-separated list of attribute column names",
    )
    bbox_wgs84: str | None = Field(default=None)
    notes: str | None = Field(default=None)
