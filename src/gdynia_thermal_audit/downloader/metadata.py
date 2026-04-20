"""Provenance metadata extraction from HTTP responses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gdynia_thermal_audit.downloader.checksums import compute_sha256
from gdynia_thermal_audit.utils.time import now_iso


def extract_metadata(response: Any, local_path: Path | None = None) -> dict[str, Any]:
    """Build a provenance metadata dict from an HTTP response.

    Parameters
    ----------
    response:
        An ``httpx.Response`` or ``requests.Response`` object.
    local_path:
        If provided, the SHA-256 checksum of the file is included.

    Returns
    -------
    Dict suitable for insertion into the source inventory.
    """
    headers = dict(response.headers) if hasattr(response, "headers") else {}

    meta: dict[str, Any] = {
        "url": str(response.url),
        "timestamp": now_iso(),
        "status_code": response.status_code,
        "content_type": headers.get("content-type", headers.get("Content-Type")),
        "content_length": headers.get("content-length", headers.get("Content-Length")),
        "last_modified": headers.get("last-modified", headers.get("Last-Modified")),
        "etag": headers.get("etag", headers.get("ETag")),
        "local_path": str(local_path) if local_path else None,
        "checksum": None,
    }

    if local_path and Path(local_path).exists():
        meta["checksum"] = compute_sha256(Path(local_path))

    return meta
