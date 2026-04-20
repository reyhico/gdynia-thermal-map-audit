"""Layer catalog record schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LayerCatalogRecord(BaseModel):
    """One row in the layer catalog CSV."""

    layer_id: str = Field(description="Unique layer identifier (LYR-NNN)")
    source_url: str = Field(description="URL of the service or file")
    service_type: str = Field(description="WMS | WMTS | WFS | GeoJSON | GeoTIFF | TILE | UNKNOWN")
    layer_name: str | None = Field(default=None, description="Machine-readable layer name")
    title: str | None = Field(default=None, description="Human-readable layer title")
    crs: str | None = Field(default=None, description="CRS identifier, e.g. EPSG:2180")
    format: str | None = Field(default=None, description="Output format, e.g. image/png")
    bbox_wgs84: str | None = Field(
        default=None,
        description="Bounding box as [lon_min, lat_min, lon_max, lat_max] string",
    )
    abstract: str | None = Field(default=None, description="Layer abstract / description")
    timestamp: str | None = Field(default=None, description="UTC ISO 8601 discovery timestamp")
    notes: str | None = Field(default=None)
