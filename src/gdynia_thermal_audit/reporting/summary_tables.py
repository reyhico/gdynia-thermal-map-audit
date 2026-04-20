"""Summary table generators for reporting."""

from __future__ import annotations

import pandas as pd


def make_source_inventory_table(source_inventory_df: pd.DataFrame) -> pd.DataFrame:
    """Build a summary table of the source inventory.

    Parameters
    ----------
    source_inventory_df:
        DataFrame conforming to the source inventory schema.

    Returns
    -------
    Summary DataFrame grouped by ``inferred_data_type`` and ``status_code``.
    """
    df = source_inventory_df.copy()

    group_cols = []
    for col in ("inferred_data_type", "status_code"):
        if col in df.columns:
            group_cols.append(col)

    if not group_cols:
        return pd.DataFrame({"count": [len(df)]})

    summary = (
        df.groupby(group_cols, dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return summary


def make_indicator_summary_table(indicators_df: pd.DataFrame) -> pd.DataFrame:
    """Build a summary statistics table for per-unit indicators.

    Parameters
    ----------
    indicators_df:
        DataFrame of per-unit indicator values.

    Returns
    -------
    Transposed describe() table for numeric indicator columns.
    """
    numeric_cols = indicators_df.select_dtypes(include="number").columns.tolist()
    # Exclude metadata columns
    exclude = {"row", "col"}
    numeric_cols = [c for c in numeric_cols if c not in exclude]

    if not numeric_cols:
        return pd.DataFrame({"message": ["No numeric indicator columns found"]})

    summary = indicators_df[numeric_cols].describe().round(4).T.rename(columns={"50%": "median"})
    return summary
