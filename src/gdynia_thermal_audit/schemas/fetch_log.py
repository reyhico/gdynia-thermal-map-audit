"""Fetch log record schema."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FetchLogRecord(BaseModel):
    """One row in the HTTP fetch log."""

    request_id: str = Field(description="Unique request identifier (REQ-NNNN)")
    url: str = Field(description="Request URL")
    method: str = Field(default="GET", description="HTTP method")
    timestamp: Optional[str] = Field(default=None, description="UTC ISO 8601 request timestamp")
    status_code: Optional[int] = Field(default=None)
    content_type: Optional[str] = Field(default=None)
    content_length: Optional[int] = Field(default=None, description="Response body size in bytes")
    duration_ms: Optional[float] = Field(default=None, description="Round-trip latency in milliseconds")
    local_path: Optional[str] = Field(default=None, description="Path where body was saved")
    checksum: Optional[str] = Field(default=None, description="SHA-256 hex digest")
    error: Optional[str] = Field(default=None, description="Error message if request failed")
    notes: Optional[str] = Field(default=None)
