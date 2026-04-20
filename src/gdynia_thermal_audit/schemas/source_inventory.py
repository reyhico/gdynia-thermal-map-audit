"""Source inventory record schema."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class SourceInventoryRecord(BaseModel):
    """One row in the source inventory CSV."""

    record_id: str = Field(description="Unique record identifier (SRC-NNN)")
    url: str = Field(description="Canonical URL of the discovered resource")
    timestamp: Optional[str] = Field(default=None, description="UTC ISO 8601 fetch timestamp")
    local_path: Optional[str] = Field(default=None, description="Relative path to downloaded file")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    content_type: Optional[str] = Field(default=None, description="MIME type from Content-Type header")
    content_length: Optional[int] = Field(default=None, description="Content-Length in bytes")
    checksum: Optional[str] = Field(default=None, description="SHA-256 hex digest of the downloaded body")
    parser_status: Optional[str] = Field(default=None, description="Result of parser pass: ok | not_found | error | skipped")
    notes: Optional[str] = Field(default=None)
    legal_ethics_note: Optional[str] = Field(default=None, description="Any access-control or legal observation")
    inferred_data_type: Optional[str] = Field(
        default=None,
        description="wms | wmts | wfs | geojson | geotiff | tile | config | html | unknown",
    )
    lineage: Optional[str] = Field(default=None, description="How this URL was discovered")
