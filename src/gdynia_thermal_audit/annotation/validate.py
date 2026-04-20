"""Annotation CSV validation."""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from gdynia_thermal_audit.constants import (
    ANOMALY_SCALE_MAX,
    ANOMALY_SCALE_MIN,
    VISIBILITY_QUALITY_MAX,
    VISIBILITY_QUALITY_MIN,
)

log = logging.getLogger("gdynia_thermal_audit.annotation.validate")

_REQUIRED_FIELDS = [
    "record_id",
    "lon",
    "lat",
    "source_url",
    "observed_anomaly",
    "visibility_quality",
    "annotator",
    "annotation_date",
]
_BOOL_FIELDS = ["observed_anomaly", "roof_flag", "facade_flag", "network_adjacent_flag"]
_DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


def validate_annotations(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate an annotation DataFrame.

    Parameters
    ----------
    df:
        Annotation records.

    Returns
    -------
    ``(is_valid, errors)`` where *errors* is a list of human-readable error messages.
    """
    errors: list[str] = []

    # Required field presence
    for col in _REQUIRED_FIELDS:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")
        elif df[col].isna().any():
            n = df[col].isna().sum()
            errors.append(f"Column '{col}' has {n} null value(s) in required field")

    # Record ID uniqueness
    if "record_id" in df.columns:
        dupes = df["record_id"].duplicated().sum()
        if dupes:
            errors.append(f"{dupes} duplicate record_id(s) found")

    # Coordinate range
    for coord_col, valid_range in [("lon", (-180, 180)), ("lat", (-90, 90))]:
        if coord_col in df.columns:
            numeric = pd.to_numeric(df[coord_col], errors="coerce")
            bad = ((numeric < valid_range[0]) | (numeric > valid_range[1])).sum()
            if bad:
                errors.append(f"{bad} out-of-range values in '{coord_col}' (expected {valid_range})")

    # anomaly_scale_1_5 range
    if "anomaly_scale_1_5" in df.columns:
        scale = pd.to_numeric(df["anomaly_scale_1_5"], errors="coerce").dropna()
        bad = ((scale < ANOMALY_SCALE_MIN) | (scale > ANOMALY_SCALE_MAX)).sum()
        if bad:
            errors.append(
                f"{bad} out-of-range anomaly_scale_1_5 values (expected {ANOMALY_SCALE_MIN}–{ANOMALY_SCALE_MAX})"
            )

    # visibility_quality range
    if "visibility_quality" in df.columns:
        vq = pd.to_numeric(df["visibility_quality"], errors="coerce").dropna()
        bad = ((vq < VISIBILITY_QUALITY_MIN) | (vq > VISIBILITY_QUALITY_MAX)).sum()
        if bad:
            errors.append(
                f"{bad} out-of-range visibility_quality values (expected {VISIBILITY_QUALITY_MIN}–{VISIBILITY_QUALITY_MAX})"
            )

    # Date format
    if "annotation_date" in df.columns:
        dates = df["annotation_date"].dropna().astype(str)
        bad = (~dates.str.match(_DATE_PATTERN)).sum()
        if bad:
            errors.append(f"{bad} annotation_date value(s) not in YYYY-MM-DD format")

    is_valid = len(errors) == 0
    if is_valid:
        log.info("Annotation validation passed for %d records", len(df))
    else:
        log.warning("Annotation validation failed: %d error(s)", len(errors))
    return is_valid, errors
