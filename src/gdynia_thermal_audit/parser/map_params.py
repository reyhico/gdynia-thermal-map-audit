"""Map parameter extraction from HTML / JavaScript."""

from __future__ import annotations

import re
from typing import Any

_CENTER_RE = re.compile(
    r"""(?:center|latlng|setView)\s*[\(=:,\[]+\s*([-\d.]+)\s*,\s*([-\d.]+)""",
    re.IGNORECASE,
)
_ZOOM_RE = re.compile(r"""(?:zoom|setZoom)\s*[\(=:]+\s*(\d+)""", re.IGNORECASE)
_CRS_RE = re.compile(
    r"""(?:crs|projection|srs)\s*[=:]\s*['"]?(EPSG:\d+|EPSG%3A\d+)['"]?""", re.IGNORECASE
)
_EXTENT_RE = re.compile(
    r"""(?:extent|bounds|bbox)\s*[=:\[]+\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)""",
    re.IGNORECASE,
)


def extract_map_params(html_or_js: str) -> dict[str, Any]:
    """Extract map initialisation parameters from HTML or JS source.

    Parameters
    ----------
    html_or_js:
        Raw HTML or JavaScript text.

    Returns
    -------
    Dict with keys: ``center_lat``, ``center_lon``, ``zoom``, ``crs``, ``extent``.
    All values may be *None* if not found.
    """
    result: dict[str, Any] = {
        "center_lat": None,
        "center_lon": None,
        "zoom": None,
        "crs": None,
        "extent": None,
    }

    m = _CENTER_RE.search(html_or_js)
    if m:
        result["center_lat"] = float(m.group(1))
        result["center_lon"] = float(m.group(2))

    m = _ZOOM_RE.search(html_or_js)
    if m:
        result["zoom"] = int(m.group(1))

    m = _CRS_RE.search(html_or_js)
    if m:
        result["crs"] = m.group(1).replace("%3A", ":").upper()

    m = _EXTENT_RE.search(html_or_js)
    if m:
        result["extent"] = [float(m.group(i)) for i in range(1, 5)]

    return result
