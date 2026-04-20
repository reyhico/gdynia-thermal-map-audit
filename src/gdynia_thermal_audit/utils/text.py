"""Text manipulation utilities."""

from __future__ import annotations

import re
import unicodedata


def slugify(s: str, separator: str = "-") -> str:
    """Convert a string to a URL/filename-safe slug.

    Parameters
    ----------
    s:
        Input string.
    separator:
        Character used to replace spaces and non-alphanumeric chars.
    """
    # Normalise unicode (decompose accented chars, then remove combining marks)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", separator, s)
    s = s.strip(separator)
    return s


def truncate(s: str, max_len: int, suffix: str = "…") -> str:
    """Truncate *s* to *max_len* characters, appending *suffix* if truncated.

    Parameters
    ----------
    s:
        Input string.
    max_len:
        Maximum length of the returned string (including *suffix*).
    suffix:
        String appended when truncation occurs.
    """
    if len(s) <= max_len:
        return s
    trunc_len = max_len - len(suffix)
    if trunc_len < 0:
        return suffix[:max_len]
    return s[:trunc_len] + suffix


def clean_whitespace(s: str) -> str:
    """Collapse multiple whitespace characters into single spaces and strip."""
    return re.sub(r"\s+", " ", s).strip()
