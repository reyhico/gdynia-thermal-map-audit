"""Viewer page snapshot."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("gdynia_thermal_audit.frontend_audit.viewer_snapshot")


def snapshot_viewer(url: str, output_dir: Path, session: Any) -> dict[str, Any]:
    """Snapshot the viewer page HTML and record metadata.

    Parameters
    ----------
    url:
        Viewer URL.
    output_dir:
        Directory where the raw HTML is saved.
    session:
        HTTP session (``httpx.Client`` or ``requests.Session``).

    Returns
    -------
    Dict with keys: ``url``, ``status_code``, ``content_type``,
    ``content_length``, ``local_path``, ``headers``.
    """
    log.info("Snapshotting viewer: %s", url)
    response = session.get(url)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "viewer_snapshot.html"
    out_path.write_text(response.text, encoding="utf-8")
    log.info("Saved viewer snapshot to %s", out_path)

    return {
        "url": url,
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "content_length": len(response.content),
        "local_path": str(out_path),
        "headers": dict(response.headers),
    }
