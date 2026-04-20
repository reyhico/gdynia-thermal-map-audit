"""Layer catalog builder aggregating discovered layers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from gdynia_thermal_audit.utils.time import now_iso


def build_layer_catalog(sources: list[dict[str, Any]]) -> pd.DataFrame:
    """Aggregate probe results into a structured layer catalog.

    Parameters
    ----------
    sources:
        List of dicts, each representing a probed URL (typically from
        ``probe_results.csv``).

    Returns
    -------
    DataFrame with columns matching :class:`~gdynia_thermal_audit.schemas.layer_catalog.LayerCatalogRecord`.
    """
    rows: list[dict[str, Any]] = []
    counter = 1

    for src in sources:
        url = src.get("url", "")
        if not url:
            continue

        service_type = _infer_service_type(src)
        rows.append(
            {
                "layer_id": f"LYR-{counter:04d}",
                "source_url": url,
                "service_type": service_type,
                "layer_name": src.get("layer_name", ""),
                "title": src.get("title", ""),
                "crs": src.get("crs", ""),
                "format": src.get("format", ""),
                "bbox_wgs84": src.get("bbox_wgs84", ""),
                "abstract": src.get("abstract", ""),
                "timestamp": src.get("timestamp", now_iso()),
                "notes": src.get("notes", ""),
            }
        )
        counter += 1

    if not rows:
        return pd.DataFrame(
            columns=[
                "layer_id",
                "source_url",
                "service_type",
                "layer_name",
                "title",
                "crs",
                "format",
                "bbox_wgs84",
                "abstract",
                "timestamp",
                "notes",
            ]
        )
    return pd.DataFrame(rows)


def _infer_service_type(src: dict[str, Any]) -> str:
    """Infer service type from probe result metadata."""
    url = src.get("url", "").upper()
    ct = (src.get("content_type") or "").lower()
    notes = (src.get("notes") or "").lower()

    if "SERVICE=WMS" in url or "ogc_xml" in notes:
        return "WMS"
    if "SERVICE=WMTS" in url:
        return "WMTS"
    if "SERVICE=WFS" in url:
        return "WFS"
    if "geojson" in ct or url.endswith(".GEOJSON"):
        return "GeoJSON"
    if "image" in ct:
        return "TILE"
    return "UNKNOWN"
