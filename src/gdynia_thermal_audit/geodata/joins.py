"""Spatial join utilities."""

from __future__ import annotations

import logging

import geopandas as gpd

log = logging.getLogger("gdynia_thermal_audit.geodata.joins")


def spatial_join(
    left_gdf: gpd.GeoDataFrame,
    right_gdf: gpd.GeoDataFrame,
    how: str = "left",
    predicate: str = "intersects",
) -> gpd.GeoDataFrame:
    """Perform a spatial join between two GeoDataFrames.

    Both GeoDataFrames are reprojected to a common CRS (from *left_gdf*)
    before joining.

    Parameters
    ----------
    left_gdf:
        Left GeoDataFrame.
    right_gdf:
        Right GeoDataFrame.
    how:
        Join type: ``'left'``, ``'right'``, or ``'inner'``.
    predicate:
        Spatial predicate: ``'intersects'``, ``'within'``, ``'contains'``, etc.

    Returns
    -------
    Joined GeoDataFrame.
    """
    if left_gdf.crs is None or right_gdf.crs is None:
        log.warning("One or both GeoDataFrames have no CRS; joining without reprojection")
    elif left_gdf.crs != right_gdf.crs:
        log.debug("Reprojecting right GeoDataFrame to match left CRS (%s)", left_gdf.crs)
        right_gdf = right_gdf.to_crs(left_gdf.crs)

    return gpd.sjoin(left_gdf, right_gdf, how=how, predicate=predicate)


def join_by_nearest(
    points_gdf: gpd.GeoDataFrame,
    polygons_gdf: gpd.GeoDataFrame,
    max_distance: float | None = None,
) -> gpd.GeoDataFrame:
    """Join each point to the nearest polygon.

    Parameters
    ----------
    points_gdf:
        GeoDataFrame of point geometries.
    polygons_gdf:
        GeoDataFrame of polygon geometries.
    max_distance:
        Maximum search distance in CRS units.  If *None*, no distance
        constraint is applied.

    Returns
    -------
    Points GeoDataFrame with polygon attributes appended.
    """
    if points_gdf.crs != polygons_gdf.crs:
        polygons_gdf = polygons_gdf.to_crs(points_gdf.crs)

    return gpd.sjoin_nearest(
        points_gdf,
        polygons_gdf,
        how="left",
        max_distance=max_distance,
        distance_col="join_distance_m",
    )
