"""Spatial metrics helpers."""

from __future__ import annotations

import logging
from typing import Sequence

import geopandas as gpd
import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.indicators.spatial_metrics")

_M2_PER_HA = 10_000.0


def compute_area_ha(gdf: gpd.GeoDataFrame) -> pd.Series:
    """Return a Series of area values in hectares for each feature.

    The GeoDataFrame must be in a projected CRS (units: metres).
    """
    if gdf.crs is None or gdf.crs.is_geographic:
        log.warning(
            "GeoDataFrame CRS is geographic; area in ha may be inaccurate. "
            "Reproject to a projected CRS first."
        )
    return gdf.geometry.area / _M2_PER_HA


def compute_centroid_coords(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """Return a DataFrame with ``centroid_x`` and ``centroid_y`` columns."""
    centroids = gdf.geometry.centroid
    return pd.DataFrame({"centroid_x": centroids.x, "centroid_y": centroids.y})


def moran_i_hint(values: Sequence[float], weights_matrix: object | None = None) -> str:
    """Return a placeholder message about spatial autocorrelation.

    Full Moran's I computation requires ``libpysal`` (Phase 2 dependency).
    """
    if weights_matrix is not None:
        return "Moran's I computation requires libpysal (Phase 2 dependency)."
    return (
        "Spatial autocorrelation (Moran's I) is a Phase 2 analysis. "
        "Placeholder spatial metrics computed."
    )
