"""CRS utilities for GeoDataFrames."""

from __future__ import annotations

import logging
from typing import Optional

import geopandas as gpd

log = logging.getLogger("gdynia_thermal_audit.geodata.crs")


def ensure_crs(gdf: gpd.GeoDataFrame, target_epsg: int) -> gpd.GeoDataFrame:
    """Reproject *gdf* to *target_epsg* if its CRS differs.

    Parameters
    ----------
    gdf:
        Input GeoDataFrame.
    target_epsg:
        Target EPSG code.

    Returns
    -------
    GeoDataFrame in the target CRS (may be the same object if already correct).
    """
    if gdf.crs is None:
        log.warning("GeoDataFrame has no CRS; assuming EPSG:4326")
        gdf = gdf.set_crs(epsg=4326)
    if gdf.crs.to_epsg() != target_epsg:
        log.debug("Reprojecting from EPSG:%d to EPSG:%d", gdf.crs.to_epsg(), target_epsg)
        gdf = gdf.to_crs(epsg=target_epsg)
    return gdf


def get_crs_info(gdf: gpd.GeoDataFrame) -> dict[str, object]:
    """Return basic CRS metadata for a GeoDataFrame."""
    crs = gdf.crs
    if crs is None:
        return {"epsg": None, "name": None, "is_geographic": None, "is_projected": None}
    return {
        "epsg": crs.to_epsg(),
        "name": crs.name,
        "is_geographic": crs.is_geographic,
        "is_projected": crs.is_projected,
    }


def is_projected(gdf: gpd.GeoDataFrame) -> bool:
    """Return *True* if *gdf* uses a projected (non-geographic) CRS."""
    if gdf.crs is None:
        return False
    return bool(gdf.crs.is_projected)
