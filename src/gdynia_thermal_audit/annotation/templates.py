"""Annotation CSV template definitions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

_ANNOTATION_COLUMNS = [
    "record_id",
    "building_id",
    "lon",
    "lat",
    "address",
    "district",
    "neighborhood",
    "spatial_unit_id",
    "source_url",
    "screenshot_ref",
    "observed_anomaly",
    "anomaly_scale_1_5",
    "apparent_area_m2",
    "roof_flag",
    "facade_flag",
    "network_adjacent_flag",
    "visibility_quality",
    "annotator",
    "annotation_date",
    "notes",
]

_COLUMN_DTYPES: dict[str, str] = {
    "record_id": "string",
    "building_id": "string",
    "lon": "float64",
    "lat": "float64",
    "address": "string",
    "district": "string",
    "neighborhood": "string",
    "spatial_unit_id": "string",
    "source_url": "string",
    "screenshot_ref": "string",
    "observed_anomaly": "boolean",
    "anomaly_scale_1_5": "Int64",
    "apparent_area_m2": "float64",
    "roof_flag": "boolean",
    "facade_flag": "boolean",
    "network_adjacent_flag": "boolean",
    "visibility_quality": "Int64",
    "annotator": "string",
    "annotation_date": "string",
    "notes": "string",
}


def get_annotation_template() -> pd.DataFrame:
    """Return an empty DataFrame with all annotation columns and correct dtypes."""
    return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in _COLUMN_DTYPES.items()})


def create_annotation_csv(output_path: Path | str, n_rows: int = 0) -> Path:
    """Create an annotation CSV template file.

    Parameters
    ----------
    output_path:
        Destination file path.
    n_rows:
        Number of empty rows to include (default: 0 — headers only).

    Returns
    -------
    Path to the created file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = get_annotation_template()
    if n_rows > 0:
        empty_rows = pd.DataFrame(
            [[None] * len(_ANNOTATION_COLUMNS)] * n_rows,
            columns=_ANNOTATION_COLUMNS,
        )
        df = pd.concat([df, empty_rows], ignore_index=True)
    df.to_csv(output_path, index=False)
    return output_path
