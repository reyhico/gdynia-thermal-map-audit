"""File download with retry logic and rate limiting."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

log = logging.getLogger("gdynia_thermal_audit.downloader.fetch")


def fetch_resource(
    url: str,
    local_path: Path,
    session: Any,
    delay: float = 1.0,
    max_retries: int = 3,
) -> bool:
    """Download *url* to *local_path* with retry and rate limiting.

    Parameters
    ----------
    url:
        URL to download.
    local_path:
        Destination file path.
    session:
        HTTP session with a ``get`` method.
    delay:
        Seconds to sleep before each attempt.
    max_retries:
        Maximum number of attempts.

    Returns
    -------
    ``True`` if the download succeeded, ``False`` otherwise.
    """
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, max_retries + 1):
        time.sleep(delay)
        try:
            response = session.get(url)
            response.raise_for_status()
            local_path.write_bytes(response.content)
            log.info("Downloaded %s → %s (%d bytes)", url, local_path, len(response.content))
            return True
        except Exception as exc:
            log.warning("Attempt %d/%d failed for %s: %s", attempt, max_retries, url, exc)
            if attempt < max_retries:
                time.sleep(delay * attempt)  # exponential back-off

    log.error("All %d attempts failed for %s", max_retries, url)
    return False
