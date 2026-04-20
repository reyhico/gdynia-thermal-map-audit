"""Raster inventory record schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RasterInventoryRecord(BaseModel):
    """Metadata for a downloaded or discovered raster file."""

    raster_id: str = Field(description="Unique raster identifier (RST-NNN)")
    local_path: Optional[str] = Field(default=None)
    source_url: Optional[str] = Field(default=None)
    crs: Optional[str] = Field(default=None, description="CRS string, e.g. EPSG:2180")
    width: Optional[int] = Field(default=None, description="Raster width in pixels")
    height: Optional[int] = Field(default=None, description="Raster height in pixels")
    bands: Optional[int] = Field(default=None, description="Number of bands")
    dtype: Optional[str] = Field(default=None, description="Numpy dtype string, e.g. float32")
    nodata: Optional[float] = Field(default=None)
    bbox_wgs84: Optional[str] = Field(default=None)
    acquisition_date: Optional[str] = Field(default=None, description="ISO 8601 acquisition date if known")
    notes: Optional[str] = Field(default=None)
