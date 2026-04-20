"""Hashing utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path | str, chunk_size: int = 65536) -> str:
    """Return the SHA-256 hex digest of a file.

    Parameters
    ----------
    path:
        File to hash.
    chunk_size:
        Read chunk size in bytes.
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(s: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_dict(d: dict[str, Any]) -> str:
    """Return the SHA-256 hex digest of a JSON-serialised dict.

    Keys are sorted to ensure deterministic hashing.
    """
    serialised = json.dumps(d, sort_keys=True, ensure_ascii=False, default=str)
    return sha256_string(serialised)
