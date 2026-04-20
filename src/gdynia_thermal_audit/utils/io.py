"""I/O utility functions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def ensure_dir(path: Path | str) -> Path:
    """Create a directory (and parents) if it does not exist.

    Parameters
    ----------
    path:
        Directory path.

    Returns
    -------
    Resolved Path object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_yaml(path: Path | str) -> dict[str, Any]:
    """Load a YAML file and return its content as a dict."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def save_yaml(data: dict[str, Any], path: Path | str) -> None:
    """Save *data* as a YAML file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)


def load_csv(path: Path | str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: Path | str, index: bool = False) -> None:
    """Save a DataFrame to CSV."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=index)


def load_json(path: Path | str) -> Any:
    """Load a JSON file."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(data: Any, path: Path | str, indent: int = 2) -> None:
    """Save *data* as a JSON file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False, default=str)
