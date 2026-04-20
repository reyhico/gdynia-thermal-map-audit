"""HTTP response header inspection utilities."""

from __future__ import annotations

from typing import Any


def inspect_headers(response: Any) -> dict[str, Any]:
    """Extract relevant metadata from an HTTP response's headers.

    Parameters
    ----------
    response:
        An ``httpx.Response`` or ``requests.Response`` object.

    Returns
    -------
    Dict with extracted metadata fields.
    """
    headers = dict(response.headers) if hasattr(response, "headers") else {}

    def _get(*keys: str) -> str | None:
        for k in keys:
            v = headers.get(k) or headers.get(k.lower()) or headers.get(k.upper())
            if v:
                return v
        return None

    return {
        "content_type": _get("content-type"),
        "content_length": _get("content-length"),
        "last_modified": _get("last-modified"),
        "etag": _get("etag"),
        "cache_control": _get("cache-control"),
        "x_powered_by": _get("x-powered-by"),
        "server": _get("server"),
        "access_control_allow_origin": _get("access-control-allow-origin"),
        "content_disposition": _get("content-disposition"),
    }
