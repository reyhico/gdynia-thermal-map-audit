"""Raster inventory record schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RasterInventoryRecord(BaseModel):
    """Metadata for a downloaded or discovered raster file."""

    raster_id: str = Field(description="Unique raster identifier (RST-NNN)")
    local_path: str | None = Field(default=None)
    source_url: str | None = Field(default=None)
    crs: str | None = Field(default=None, description="CRS string, e.g. EPSG:2180")
    width: int | None = Field(default=None, description="Raster width in pixels")
    height: int | None = Field(default=None, description="Raster height in pixels")
    bands: int | None = Field(default=None, description="Number of bands")
    dtype: str | None = Field(default=None, description="Numpy dtype string, e.g. float32")
    nodata: float | None = Field(default=None)
    bbox_wgs84: str | None = Field(default=None)
    acquisition_date: str | None = Field(
        default=None, description="ISO 8601 acquisition date if known"
    )
    notes: str | None = Field(default=None)
