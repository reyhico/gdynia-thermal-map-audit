"""Annotation-based thermal indicators (Scenario C)."""

from __future__ import annotations

import logging

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

log = logging.getLogger("gdynia_thermal_audit.indicators.annotation_indicators")

_M2_PER_HA = 10_000.0


def compute_annotation_indicators(
    zones_gdf: gpd.GeoDataFrame,
    annotations_df: pd.DataFrame,
    unit_id_col: str = "district_id",
    lon_col: str = "lon",
    lat_col: str = "lat",
) -> pd.DataFrame:
    """Compute thermal indicators from manual annotation records.

    Parameters
    ----------
    zones_gdf:
        Spatial unit GeoDataFrame in any CRS.
    annotations_df:
        DataFrame of annotation records (see annotation template).
    unit_id_col:
        Column in *zones_gdf* to use as unit identifier.
    lon_col, lat_col:
        Column names for WGS-84 coordinates in *annotations_df*.

    Returns
    -------
    DataFrame with one row per spatial unit.
    """
    # Build annotation GeoDataFrame in EPSG:4326
    valid_ann = annotations_df.dropna(subset=[lon_col, lat_col]).copy()
    if valid_ann.empty:
        log.warning("No valid coordinate records in annotations")
        return _empty_result(zones_gdf, unit_id_col)

    ann_gdf = gpd.GeoDataFrame(
        valid_ann,
        geometry=[Point(row[lon_col], row[lat_col]) for _, row in valid_ann.iterrows()],
        crs="EPSG:4326",
    )

    # Reproject to match zones
    if zones_gdf.crs is None:
        zones_gdf = zones_gdf.set_crs(epsg=4326)
    ann_gdf = ann_gdf.to_crs(zones_gdf.crs)

    id_col = unit_id_col if unit_id_col in zones_gdf.columns else zones_gdf.columns[0]

    rows = []
    for _, zone in zones_gdf.iterrows():
        geom = zone.geometry
        unit_id = zone[id_col]
        in_zone = ann_gdf[ann_gdf.geometry.within(geom)]

        anomaly_mask = in_zone["observed_anomaly"].astype(str).str.lower().isin(
            ("true", "1", "yes", "t")
        )
        anomaly_recs = in_zone[anomaly_mask]

        n_total = len(in_zone)
        n_anomaly = len(anomaly_recs)
        area_ha = geom.area / _M2_PER_HA if geom is not None else None

        mean_intensity: float | None = None
        if "anomaly_scale_1_5" in anomaly_recs.columns:
            scales = pd.to_numeric(anomaly_recs["anomaly_scale_1_5"], errors="coerce").dropna()
            if not scales.empty:
                # Normalise 1-5 scale to 0-1
                mean_intensity = float((scales.mean() - 1) / 4)

        rows.append(
            {
                "unit_id": unit_id,
                "annotation_count": n_total,
                "anomaly_count": n_anomaly,
                "anomaly_density_per_ha": (
                    round(n_anomaly / area_ha, 4) if area_ha and area_ha > 0 else None
                ),
                "mean_intensity": round(mean_intensity, 4) if mean_intensity is not None else None,
                "building_anomaly_count": int(
                    anomaly_recs.get("roof_flag", pd.Series(dtype=bool))
                    .astype(str)
                    .str.lower()
                    .isin(("true", "1"))
                    .sum()
                )
                if "roof_flag" in anomaly_recs.columns
                else None,
                "data_source": "annotation",
            }
        )

    return pd.DataFrame(rows)


def _empty_result(zones_gdf: gpd.GeoDataFrame, unit_id_col: str) -> pd.DataFrame:
    id_col = unit_id_col if unit_id_col in zones_gdf.columns else zones_gdf.columns[0]
    return pd.DataFrame(
        [
            {
                "unit_id": row[id_col],
                "annotation_count": 0,
                "anomaly_count": 0,
                "anomaly_density_per_ha": None,
                "mean_intensity": None,
                "building_anomaly_count": None,
                "data_source": "annotation",
            }
            for _, row in zones_gdf.iterrows()
        ]
    )
