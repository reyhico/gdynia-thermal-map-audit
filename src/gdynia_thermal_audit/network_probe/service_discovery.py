"""Service discovery: iterate candidate URLs and categorise them."""

from __future__ import annotations

import logging
from typing import Any

from gdynia_thermal_audit.network_probe.endpoint_probe import ProbeResult, probe_endpoint

log = logging.getLogger("gdynia_thermal_audit.network_probe.service_discovery")

# Well-known OGC/geospatial URL suffixes to try
_OGC_SUFFIXES = [
    "/wms?SERVICE=WMS&REQUEST=GetCapabilities",
    "/wmts?SERVICE=WMTS&REQUEST=GetCapabilities",
    "/wfs?SERVICE=WFS&REQUEST=GetCapabilities",
    "/ows?SERVICE=WMS&REQUEST=GetCapabilities",
    "/geoserver/wms?SERVICE=WMS&REQUEST=GetCapabilities",
    "/arcgis/rest/services?f=json",
]


def discover_services(
    candidate_urls: list[str],
    session: Any | None = None,
    delay: float = 1.0,
    probe_ogc_suffixes: bool = False,
) -> list[ProbeResult]:
    """Probe a list of candidate URLs and return :class:`ProbeResult` objects.

    Parameters
    ----------
    candidate_urls:
        URLs to probe.
    session:
        Optional HTTP session.  If *None*, a new ``httpx.Client`` is created.
    delay:
        Per-request delay in seconds.
    probe_ogc_suffixes:
        If *True*, also probe well-known OGC suffixes derived from each base URL.
    """
    import httpx

    owns_session = session is None
    if owns_session:
        session = httpx.Client(timeout=30, follow_redirects=True)

    all_urls = list(candidate_urls)
    if probe_ogc_suffixes:
        bases = {_extract_base(u) for u in candidate_urls}
        for base in bases:
            for suffix in _OGC_SUFFIXES:
                all_urls.append(base + suffix)

    results: list[ProbeResult] = []
    try:
        for url in all_urls:
            result = probe_endpoint(url, session, delay=delay)
            result.notes = _categorise(result)
            results.append(result)
    finally:
        if owns_session:
            session.close()

    log.info(
        "Probed %d URLs; %d returned HTTP 200",
        len(results),
        sum(r.status_code == 200 for r in results),
    )
    return results


def _extract_base(url: str) -> str:
    """Return the scheme + host portion of a URL."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _categorise(result: ProbeResult) -> str:
    """Assign a human-readable category to a probe result."""
    if result.error:
        return "error"
    ct = (result.content_type or "").lower()
    if "xml" in ct or "wms_xml" in ct:
        return "ogc_xml"
    if "json" in ct:
        return "json"
    if "html" in ct:
        return "html"
    if "image" in ct:
        return "image"
    return "other"
