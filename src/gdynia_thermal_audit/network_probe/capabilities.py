"""OGC capabilities parsing helpers."""

from __future__ import annotations

import logging
from typing import Any, Optional

log = logging.getLogger("gdynia_thermal_audit.network_probe.capabilities")


def fetch_wms_capabilities(url: str, session: Any) -> Optional[dict[str, Any]]:
    """Fetch and parse WMS GetCapabilities.

    Parameters
    ----------
    url:
        Base WMS URL (without query string) or full capabilities URL.
    session:
        HTTP session.

    Returns
    -------
    Dict with keys ``layers``, ``version``, ``title``, ``abstract`` or *None*
    on failure.
    """
    caps_url = _ensure_caps_url(url, "WMS")
    log.info("Fetching WMS capabilities: %s", caps_url)
    try:
        from owslib.wms import WebMapService

        wms = WebMapService(caps_url, version="1.3.0")
        layers = [
            {
                "name": name,
                "title": layer.title,
                "crs": list(layer.crsOptions),
                "bbox": layer.boundingBox,
                "abstract": layer.abstract or "",
            }
            for name, layer in wms.contents.items()
        ]
        return {
            "service": "WMS",
            "url": caps_url,
            "version": wms.identification.version,
            "title": wms.identification.title,
            "abstract": wms.identification.abstract or "",
            "layers": layers,
        }
    except Exception as exc:
        log.warning("WMS capabilities failed for %s: %s", caps_url, exc)
        return None


def fetch_wmts_capabilities(url: str, session: Any) -> Optional[dict[str, Any]]:
    """Fetch and parse WMTS GetCapabilities."""
    caps_url = _ensure_caps_url(url, "WMTS")
    log.info("Fetching WMTS capabilities: %s", caps_url)
    try:
        from owslib.wmts import WebMapTileService

        wmts = WebMapTileService(caps_url)
        layers = [
            {
                "name": name,
                "title": layer.title,
                "formats": layer.formats,
                "bbox": None,
            }
            for name, layer in wmts.contents.items()
        ]
        return {
            "service": "WMTS",
            "url": caps_url,
            "title": wmts.identification.title,
            "layers": layers,
        }
    except Exception as exc:
        log.warning("WMTS capabilities failed for %s: %s", caps_url, exc)
        return None


def fetch_wfs_capabilities(url: str, session: Any) -> Optional[dict[str, Any]]:
    """Fetch and parse WFS GetCapabilities."""
    caps_url = _ensure_caps_url(url, "WFS")
    log.info("Fetching WFS capabilities: %s", caps_url)
    try:
        from owslib.wfs import WebFeatureService

        wfs = WebFeatureService(caps_url, version="2.0.0")
        feature_types = [
            {
                "name": name,
                "title": ft.title,
                "bbox": ft.boundingBoxWGS84,
                "crs": str(ft.crsOptions[0]) if ft.crsOptions else None,
            }
            for name, ft in wfs.contents.items()
        ]
        return {
            "service": "WFS",
            "url": caps_url,
            "version": wfs.identification.version,
            "title": wfs.identification.title,
            "feature_types": feature_types,
        }
    except Exception as exc:
        log.warning("WFS capabilities failed for %s: %s", caps_url, exc)
        return None


def _ensure_caps_url(url: str, service: str) -> str:
    """Append GetCapabilities query params if not already present."""
    if "REQUEST=GetCapabilities" in url.upper():
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}SERVICE={service}&REQUEST=GetCapabilities"
