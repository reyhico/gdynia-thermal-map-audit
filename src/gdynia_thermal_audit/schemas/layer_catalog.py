"""Layer catalog record schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LayerCatalogRecord(BaseModel):
    """One row in the layer catalog CSV."""

    layer_id: str = Field(description="Unique layer identifier (LYR-NNN)")
    source_url: str = Field(description="URL of the service or file")
    service_type: str = Field(description="WMS | WMTS | WFS | GeoJSON | GeoTIFF | TILE | UNKNOWN")
    layer_name: Optional[str] = Field(default=None, description="Machine-readable layer name")
    title: Optional[str] = Field(default=None, description="Human-readable layer title")
    crs: Optional[str] = Field(default=None, description="CRS identifier, e.g. EPSG:2180")
    format: Optional[str] = Field(default=None, description="Output format, e.g. image/png")
    bbox_wgs84: Optional[str] = Field(
        default=None,
        description="Bounding box as [lon_min, lat_min, lon_max, lat_max] string",
    )
    abstract: Optional[str] = Field(default=None, description="Layer abstract / description")
    timestamp: Optional[str] = Field(default=None, description="UTC ISO 8601 discovery timestamp")
    notes: Optional[str] = Field(default=None)
