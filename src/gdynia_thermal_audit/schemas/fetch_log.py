"""Fetch log record schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FetchLogRecord(BaseModel):
    """One row in the HTTP fetch log."""

    request_id: str = Field(description="Unique request identifier (REQ-NNNN)")
    url: str = Field(description="Request URL")
    method: str = Field(default="GET", description="HTTP method")
    timestamp: str | None = Field(default=None, description="UTC ISO 8601 request timestamp")
    status_code: int | None = Field(default=None)
    content_type: str | None = Field(default=None)
    content_length: int | None = Field(default=None, description="Response body size in bytes")
    duration_ms: float | None = Field(
        default=None, description="Round-trip latency in milliseconds"
    )
    local_path: str | None = Field(default=None, description="Path where body was saved")
    checksum: str | None = Field(default=None, description="SHA-256 hex digest")
    error: str | None = Field(default=None, description="Error message if request failed")
    notes: str | None = Field(default=None)
