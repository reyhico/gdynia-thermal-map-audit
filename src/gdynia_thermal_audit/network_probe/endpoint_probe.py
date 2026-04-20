"""HTTP endpoint probing."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

log = logging.getLogger("gdynia_thermal_audit.network_probe.endpoint_probe")


@dataclass
class ProbeResult:
    """Result of probing a single HTTP endpoint."""

    url: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    last_modified: Optional[str] = None
    redirect_url: Optional[str] = None
    latency_ms: Optional[float] = None
    notes: str = ""
    error: Optional[str] = None


def probe_endpoint(
    url: str,
    session: Any,
    delay: float = 1.0,
) -> ProbeResult:
    """Probe a single URL and return a :class:`ProbeResult`.

    Attempts HEAD first; falls back to GET if the server returns 405.

    Parameters
    ----------
    url:
        URL to probe.
    session:
        HTTP session with a ``head`` and ``get`` method.
    delay:
        Seconds to wait *before* making the request (rate limiting).
    """
    time.sleep(delay)
    try:
        t0 = time.monotonic()
        resp = session.head(url, follow_redirects=True)
        if resp.status_code == 405:
            resp = session.get(url, follow_redirects=True)
        elapsed_ms = (time.monotonic() - t0) * 1000

        redirect_url: Optional[str] = None
        if resp.history:
            redirect_url = str(resp.url)

        result = ProbeResult(
            url=url,
            status_code=resp.status_code,
            content_type=resp.headers.get("content-type"),
            content_length=_parse_content_length(resp.headers.get("content-length")),
            last_modified=resp.headers.get("last-modified"),
            redirect_url=redirect_url,
            latency_ms=round(elapsed_ms, 1),
        )
        log.debug("Probed %s → %s", url, resp.status_code)
        return result

    except Exception as exc:
        log.warning("Error probing %s: %s", url, exc)
        return ProbeResult(url=url, error=str(exc))


def _parse_content_length(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
