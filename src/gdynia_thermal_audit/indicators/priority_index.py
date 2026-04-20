"""Priority index computation."""

from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.indicators.priority_index")

_DEFAULT_WEIGHTS = {
    "anomalous_area_share": 0.30,
    "anomaly_density_per_ha": 0.25,
    "building_anomaly_share": 0.25,
    "mean_intensity": 0.20,
}


def compute_priority_index(
    indicators_df: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Compute a normalised composite priority index.

    The index is a weighted sum of z-score standardised component indicators.
    Missing values are imputed with the column mean before standardisation.

    Parameters
    ----------
    indicators_df:
        DataFrame of per-unit indicators (output of any ``compute_*_indicators``).
    weights:
        Dict mapping indicator column names to numeric weights.  Columns not
        present in *indicators_df* are silently skipped.  Defaults to
        ``_DEFAULT_WEIGHTS``.

    Returns
    -------
    *indicators_df* with an additional ``priority_index`` column (float, higher = higher priority).
    """
    if weights is None:
        weights = _DEFAULT_WEIGHTS

    df = indicators_df.copy()
    available_components = {k: v for k, v in weights.items() if k in df.columns}

    if not available_components:
        log.warning(
            "None of the weight keys (%s) found in indicators DataFrame columns (%s); "
            "setting priority_index to NaN",
            list(weights.keys()),
            list(df.columns),
        )
        df["priority_index"] = float("nan")
        return df

    # Build a sub-DataFrame of component columns, imputed with column mean
    component_df = df[list(available_components.keys())].copy()
    for col in component_df.columns:
        component_df[col] = pd.to_numeric(component_df[col], errors="coerce")
        col_mean = component_df[col].mean()
        component_df[col] = component_df[col].fillna(col_mean if not pd.isna(col_mean) else 0.0)

    # Z-score standardise
    z_df = (component_df - component_df.mean()) / component_df.std(ddof=0).replace(0, 1)

    # Weighted sum
    total_weight = sum(available_components.values())
    priority = sum(z_df[col] * (w / total_weight) for col, w in available_components.items())

    df["priority_index"] = priority.round(4)
    log.info(
        "Priority index computed from %d components: %s",
        len(available_components),
        list(available_components.keys()),
    )
    return df
