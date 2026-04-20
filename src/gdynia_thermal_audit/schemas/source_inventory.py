"""Source inventory record schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SourceInventoryRecord(BaseModel):
    """One row in the source inventory CSV."""

    record_id: str = Field(description="Unique record identifier (SRC-NNN)")
    url: str = Field(description="Canonical URL of the discovered resource")
    timestamp: str | None = Field(default=None, description="UTC ISO 8601 fetch timestamp")
    local_path: str | None = Field(default=None, description="Relative path to downloaded file")
    status_code: int | None = Field(default=None, description="HTTP status code")
    content_type: str | None = Field(
        default=None, description="MIME type from Content-Type header"
    )
    content_length: int | None = Field(default=None, description="Content-Length in bytes")
    checksum: str | None = Field(
        default=None, description="SHA-256 hex digest of the downloaded body"
    )
    parser_status: str | None = Field(
        default=None, description="Result of parser pass: ok | not_found | error | skipped"
    )
    notes: str | None = Field(default=None)
    legal_ethics_note: str | None = Field(
        default=None, description="Any access-control or legal observation"
    )
    inferred_data_type: str | None = Field(
        default=None,
        description="wms | wmts | wfs | geojson | geotiff | tile | config | html | unknown",
    )
    lineage: str | None = Field(default=None, description="How this URL was discovered")
