"""SHA-256 checksum utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_sha256(filepath: Path, chunk_size: int = 65536) -> str:
    """Return the SHA-256 hex digest of a file.

    Parameters
    ----------
    filepath:
        Path to the file to hash.
    chunk_size:
        Read chunk size in bytes.
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()
