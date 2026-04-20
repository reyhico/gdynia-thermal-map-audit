"""Time and date utilities."""

from __future__ import annotations

import datetime


def now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string with Z suffix."""
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime.datetime:
    """Parse an ISO 8601 timestamp string to a ``datetime`` object (UTC assumed).

    Parameters
    ----------
    s:
        ISO 8601 string, e.g. ``"2024-06-01T08:00:00Z"`` or ``"2024-06-01"``.
    """
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse ISO timestamp: '{s}'")


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as a human-readable string.

    Parameters
    ----------
    seconds:
        Duration in seconds.

    Examples
    --------
    >>> format_duration(3661.5)
    '1h 01m 01s'
    >>> format_duration(90.3)
    '1m 30s'
    >>> format_duration(5.7)
    '5.7s'
    """
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60

    if h > 0:
        return f"{h}h {m:02d}m {int(s):02d}s"
    if m > 0:
        return f"{m}m {int(s):02d}s"
    return f"{s:.1f}s"
