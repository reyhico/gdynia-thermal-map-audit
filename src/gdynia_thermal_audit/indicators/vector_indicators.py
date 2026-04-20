"""Vector-based thermal indicators (Scenario B)."""

from __future__ import annotations

import logging

import geopandas as gpd
import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.indicators.vector_indicators")

_M2_PER_HA = 10_000.0


def compute_vector_indicators(
    zones_gdf: gpd.GeoDataFrame,
    features_gdf: gpd.GeoDataFrame,
    unit_id_col: str = "district_id",
    building_flag_col: str | None = "building",
) -> pd.DataFrame:
    """Compute vector-based thermal indicators per spatial zone.

    Indicators computed:
    - ``anomaly_count``: number of anomaly features intersecting the zone
    - ``anomaly_density_per_ha``: anomaly count per hectare of zone area
    - ``building_anomaly_count``: count of features flagged as building anomalies
    - ``building_anomaly_share``: building anomaly count / anomaly count

    Parameters
    ----------
    zones_gdf:
        Spatial unit GeoDataFrame.
    features_gdf:
        Anomaly feature GeoDataFrame (points or polygons).
    unit_id_col:
        Column in *zones_gdf* to use as unit identifier.
    building_flag_col:
        Optional column in *features_gdf* indicating building features.
    """
    # Ensure CRS alignment
    if zones_gdf.crs != features_gdf.crs:
        features_gdf = features_gdf.to_crs(zones_gdf.crs)

    id_col = unit_id_col if unit_id_col in zones_gdf.columns else zones_gdf.columns[0]

    rows = []
    for _, zone in zones_gdf.iterrows():
        geom = zone.geometry
        unit_id = zone[id_col]

        # Spatial filter
        intersecting = features_gdf[features_gdf.geometry.intersects(geom)]

        anomaly_count = len(intersecting)
        area_ha = geom.area / _M2_PER_HA if geom is not None else None
        density = anomaly_count / area_ha if area_ha and area_ha > 0 else None

        building_count = 0
        if building_flag_col and building_flag_col in intersecting.columns:
            building_count = int(intersecting[building_flag_col].notna().sum())

        rows.append(
            {
                "unit_id": unit_id,
                "anomaly_count": anomaly_count,
                "anomaly_density_per_ha": round(density, 4) if density is not None else None,
                "building_anomaly_count": building_count,
                "building_anomaly_share": (
                    round(building_count / anomaly_count, 4) if anomaly_count > 0 else 0.0
                ),
                "data_source": "vector",
            }
        )

    return pd.DataFrame(rows)
