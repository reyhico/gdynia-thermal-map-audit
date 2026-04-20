"""Annotation record merging."""

from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.annotation.merge")


def merge_annotations(
    existing_df: pd.DataFrame,
    new_df: pd.DataFrame,
    id_col: str = "record_id",
    conflict_action: str = "keep_existing",
) -> pd.DataFrame:
    """Merge new annotation records into the existing set.

    Parameters
    ----------
    existing_df:
        Existing annotation DataFrame.
    new_df:
        New records to merge.
    id_col:
        Column used to detect duplicates.
    conflict_action:
        How to handle duplicate ``record_id`` values:
        - ``'keep_existing'`` (default): keep the row already in *existing_df*.
        - ``'keep_new'``: overwrite with the new row.

    Returns
    -------
    Merged DataFrame, sorted by *id_col*.
    """
    if existing_df.empty:
        return new_df.copy()
    if new_df.empty:
        return existing_df.copy()

    # Find overlapping IDs
    existing_ids = set(existing_df[id_col].dropna())
    new_ids = set(new_df[id_col].dropna())
    overlap = existing_ids & new_ids

    if overlap:
        log.warning("%d conflicting record_id(s) detected: %s", len(overlap), sorted(overlap)[:5])

    if conflict_action == "keep_existing":
        # Exclude overlapping IDs from new_df
        new_unique = new_df[~new_df[id_col].isin(overlap)]
    elif conflict_action == "keep_new":
        # Exclude overlapping IDs from existing_df
        existing_df = existing_df[~existing_df[id_col].isin(overlap)]
        new_unique = new_df
    else:
        raise ValueError(f"Unknown conflict_action: '{conflict_action}'")

    merged = pd.concat([existing_df, new_unique], ignore_index=True)
    if id_col in merged.columns:
        merged = merged.sort_values(id_col, ignore_index=True)
    log.info(
        "Merge complete: %d existing + %d new → %d total",
        len(existing_df),
        len(new_unique),
        len(merged),
    )
    return merged
