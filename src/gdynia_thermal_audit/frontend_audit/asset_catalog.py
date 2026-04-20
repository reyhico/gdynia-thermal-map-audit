"""Asset catalog builder."""

from __future__ import annotations

from typing import Any

import pandas as pd


def build_asset_catalog(audit_results: dict[str, Any]) -> pd.DataFrame:
    """Build a structured asset catalog DataFrame from audit results.

    Parameters
    ----------
    audit_results:
        Dict returned by :func:`audit_landing_page` (or equivalent).

    Returns
    -------
    DataFrame with columns:
        url, asset_type, content_type, size, local_path, checksum, notes
    """
    rows: list[dict[str, Any]] = []

    for script in audit_results.get("scripts", []):
        if script.get("src"):
            rows.append(
                {
                    "url": script["src"],
                    "asset_type": "script",
                    "content_type": "application/javascript",
                    "size": None,
                    "local_path": None,
                    "checksum": None,
                    "notes": "candidate" if script.get("candidate") else "",
                }
            )

    for link in audit_results.get("links", []):
        if link.get("href"):
            rows.append(
                {
                    "url": link["href"],
                    "asset_type": _classify_link(link),
                    "content_type": link.get("type", ""),
                    "size": None,
                    "local_path": None,
                    "checksum": None,
                    "notes": link.get("rel", ""),
                }
            )

    for img in audit_results.get("images", []):
        if img.get("src"):
            rows.append(
                {
                    "url": img["src"],
                    "asset_type": "image",
                    "content_type": "image/*",
                    "size": None,
                    "local_path": None,
                    "checksum": None,
                    "notes": img.get("alt", ""),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "url",
                "asset_type",
                "content_type",
                "size",
                "local_path",
                "checksum",
                "notes",
            ]
        )
    return pd.DataFrame(rows)


def _classify_link(link: dict[str, Any]) -> str:
    """Classify a ``<link>`` tag by its rel/type attributes."""
    rel = " ".join(link.get("rel", "")).lower()
    href = str(link.get("href", "")).lower()
    if "stylesheet" in rel:
        return "stylesheet"
    if "icon" in rel:
        return "favicon"
    if href.endswith(".geojson"):
        return "geojson"
    if href.endswith((".tif", ".tiff", ".geotiff")):
        return "geotiff"
    return "link"
