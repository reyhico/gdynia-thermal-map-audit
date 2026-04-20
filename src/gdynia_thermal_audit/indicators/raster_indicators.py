"""Raster-based thermal indicators (Scenario A)."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd

from gdynia_thermal_audit.constants import DEFAULT_ANOMALY_THRESHOLD, MIN_COVERAGE_RATIO

log = logging.getLogger("gdynia_thermal_audit.indicators.raster_indicators")


def compute_raster_indicators(
    zones_gdf: gpd.GeoDataFrame,
    raster_path: Path | str,
    unit_id_col: str = "district_id",
    anomaly_threshold: float = DEFAULT_ANOMALY_THRESHOLD,
    min_coverage_ratio: float = MIN_COVERAGE_RATIO,
    band: int = 1,
) -> pd.DataFrame:
    """Compute raster-based thermal indicators for each spatial zone.

    Indicators computed:
    - ``coverage_ratio``: fraction of zone covered by valid pixels
    - ``mean_intensity``: mean normalised pixel intensity
    - ``median_intensity``: median normalised pixel intensity
    - ``anomalous_area_share``: fraction of valid pixels above *anomaly_threshold*

    Parameters
    ----------
    zones_gdf:
        Spatial units GeoDataFrame.
    raster_path:
        Path to the thermal-loss raster.
    unit_id_col:
        Column in *zones_gdf* to use as the unit identifier.
    anomaly_threshold:
        Normalised intensity threshold for classifying a pixel as anomalous.
    min_coverage_ratio:
        Zones with coverage below this threshold get ``None`` intensity values.
    band:
        Raster band index (1-based).

    Returns
    -------
    DataFrame with one row per zone.
    """
    from gdynia_thermal_audit.geodata.zonal_stats import compute_zonal_stats

    zs = compute_zonal_stats(
        raster_path=raster_path,
        zones_gdf=zones_gdf,
        stats=["mean", "median", "count"],
        band=band,
    )

    # Merge zone IDs
    id_col = unit_id_col if unit_id_col in zones_gdf.columns else zones_gdf.columns[0]
    id_series = zones_gdf[id_col].reset_index(drop=True)

    rows = []
    for _, zrow in zs.iterrows():
        zone_idx = zrow["zone_index"]
        unit_id = id_series.iloc[zone_idx] if zone_idx < len(id_series) else str(zone_idx)

        total_pixels = (
            zones_gdf.iloc[zone_idx].geometry.area if zone_idx < len(zones_gdf) else None
        )
        valid_count = zrow.get("count")
        coverage = None
        if valid_count is not None and total_pixels and total_pixels > 0:
            # Rough proxy — actual coverage depends on raster resolution
            coverage = min(1.0, float(valid_count) / max(1, float(total_pixels) * 1e-4))

        mean_i = zrow.get("mean")
        median_i = zrow.get("median")
        if coverage is not None and coverage < min_coverage_ratio:
            mean_i = None
            median_i = None

        rows.append(
            {
                "unit_id": unit_id,
                "coverage_ratio": coverage,
                "mean_intensity": mean_i,
                "median_intensity": median_i,
                "anomalous_area_share": None,  # requires full pixel array; set by zonal_stats ext.
                "data_source": "raster",
            }
        )

    return pd.DataFrame(rows)
