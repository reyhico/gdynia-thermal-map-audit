"""URL extraction and classification utilities."""

from __future__ import annotations

import re

_URL_RE = re.compile(
    r"""https?://[^\s<>"')\]\\]+""",
    re.IGNORECASE,
)

_GEOSPATIAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "wms": re.compile(r"SERVICE=WMS", re.IGNORECASE),
    "wmts": re.compile(r"SERVICE=WMTS", re.IGNORECASE),
    "wfs": re.compile(r"SERVICE=WFS", re.IGNORECASE),
    "geojson": re.compile(r"\.geojson(\?|$)", re.IGNORECASE),
    "geotiff": re.compile(r"\.(tif|tiff|geotiff|jp2)(\?|$)", re.IGNORECASE),
    "shapefile": re.compile(r"\.(shp|zip)(\?|$)", re.IGNORECASE),
    "tile": re.compile(r"/\{z\}/\{x\}/\{y\}|/[0-9]+/[0-9]+/[0-9]+\.(png|jpg|jpeg|webp)"),
    "config": re.compile(r"\.(json|yaml|yml|xml)(\?|$)", re.IGNORECASE),
}


def extract_urls(text: str) -> list[str]:
    """Extract all HTTP/HTTPS URLs from *text*.

    Parameters
    ----------
    text:
        Any text (HTML, JS, plain text).

    Returns
    -------
    List of unique URL strings preserving order of first occurrence.
    """
    seen: set[str] = set()
    urls: list[str] = []
    for m in _URL_RE.finditer(text):
        u = m.group(0).rstrip(".,;:")
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def classify_url(url: str) -> str:
    """Classify a URL into a geospatial service type.

    Returns one of: ``wms``, ``wmts``, ``wfs``, ``geojson``, ``geotiff``,
    ``shapefile``, ``tile``, ``config``, ``unknown``.
    """
    for service_type, pattern in _GEOSPATIAL_PATTERNS.items():
        if pattern.search(url):
            return service_type
    return "unknown"


def extract_geospatial_urls(text: str) -> list[dict[str, str]]:
    """Extract and classify only geospatial URLs from *text*.

    Returns
    -------
    List of dicts with keys ``url`` and ``type``.
    """
    all_urls = extract_urls(text)
    result = []
    for url in all_urls:
        t = classify_url(url)
        if t != "unknown":
            result.append({"url": url, "type": t})
    return result
