"""Vector data loading and validation utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.geodata.vector_utils")


def load_vector(path: Path | str, target_epsg: int | None = None) -> gpd.GeoDataFrame:
    """Load a vector file and optionally reproject it.

    Parameters
    ----------
    path:
        Path to a GeoJSON, GPKG, SHP, or other OGR-compatible file.
    target_epsg:
        If provided, reproject to this EPSG code.

    Returns
    -------
    GeoDataFrame with valid geometries.
    """
    gdf = gpd.read_file(path)
    log.info("Loaded %d features from %s (CRS: %s)", len(gdf), path, gdf.crs)

    if gdf.crs is None:
        log.warning("No CRS in %s; assuming EPSG:4326", path)
        gdf = gdf.set_crs(epsg=4326)

    if target_epsg and gdf.crs.to_epsg() != target_epsg:
        gdf = gdf.to_crs(epsg=target_epsg)

    gdf = validate_geometry(gdf)
    return gdf


def normalize_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Lowercase and strip all non-geometry column names."""
    rename_map = {
        col: col.strip().lower().replace(" ", "_")
        for col in gdf.columns
        if col != gdf.geometry.name
    }
    return gdf.rename(columns=rename_map)


def validate_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Drop null or empty geometries and log the count removed."""
    before = len(gdf)
    gdf = gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty].copy()
    removed = before - len(gdf)
    if removed:
        log.warning("Removed %d null/empty geometries", removed)
    return gdf
