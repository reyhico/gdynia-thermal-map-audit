"""Neighborhood spatial unit loader."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd

log = logging.getLogger("gdynia_thermal_audit.spatial_units.neighborhoods")


def load_neighborhoods(path: Path | str) -> gpd.GeoDataFrame:
    """Load neighborhood boundaries from a GeoJSON or GPKG file.

    Parameters
    ----------
    path:
        Path to the vector file.

    Returns
    -------
    GeoDataFrame with at least a ``geometry`` column.
    """
    gdf = gpd.read_file(path)
    log.info("Loaded %d neighborhoods from %s", len(gdf), path)
    if "neighborhood_id" not in gdf.columns:
        gdf["neighborhood_id"] = [f"NBH-{i + 1:04d}" for i in range(len(gdf))]
    if gdf.crs is None:
        log.warning("No CRS found; assuming EPSG:4326")
        gdf = gdf.set_crs(epsg=4326)
    return gdf


def validate_neighborhoods(gdf: gpd.GeoDataFrame) -> None:
    """Raise if the GeoDataFrame fails basic neighborhood validity checks."""
    if len(gdf) == 0:
        raise ValueError("Neighborhoods GeoDataFrame is empty")
    if gdf.geometry.isna().any():
        raise ValueError("Some neighborhood geometries are null")
    if not all(gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])):
        raise ValueError("All neighborhood geometries must be Polygon or MultiPolygon")
    log.info("Neighborhood validation passed (%d units)", len(gdf))
