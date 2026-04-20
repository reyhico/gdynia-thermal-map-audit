"""District spatial unit loader."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Polygon

log = logging.getLogger("gdynia_thermal_audit.spatial_units.districts")

_REQUIRED_COLUMNS = {"geometry"}


def load_districts(path: Path | str) -> gpd.GeoDataFrame:
    """Load district boundaries from a GeoJSON or GPKG file.

    Parameters
    ----------
    path:
        Path to the vector file.

    Returns
    -------
    GeoDataFrame with at least a ``geometry`` column.
    """
    gdf = gpd.read_file(path)
    log.info("Loaded %d districts from %s", len(gdf), path)
    if "district_id" not in gdf.columns:
        gdf["district_id"] = [f"GDY-{i+1:02d}" for i in range(len(gdf))]
    if gdf.crs is None:
        log.warning("No CRS found; assuming EPSG:4326")
        gdf = gdf.set_crs(epsg=4326)
    return gdf


def validate_districts(gdf: gpd.GeoDataFrame) -> None:
    """Raise if the GeoDataFrame fails basic district validity checks."""
    if len(gdf) == 0:
        raise ValueError("Districts GeoDataFrame is empty")
    if gdf.geometry.isna().any():
        raise ValueError("Some district geometries are null")
    if not all(gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])):
        raise ValueError("All district geometries must be Polygon or MultiPolygon")
    log.info("District validation passed (%d units)", len(gdf))


def get_gdynia_districts_placeholder() -> gpd.GeoDataFrame:
    """Return a minimal synthetic GeoDataFrame of Gdynia district polygons.

    Used as a fallback when no official boundary file is available.
    Geometries are approximate rectangles in EPSG:4326.
    """
    records = [
        {
            "district_id": "GDY-01",
            "name": "Śródmieście",
            "area_ha": 320.5,
            "geometry": Polygon([(18.520, 54.510), (18.560, 54.510), (18.560, 54.535), (18.520, 54.535)]),
        },
        {
            "district_id": "GDY-02",
            "name": "Wzgórze Św. Maksymiliana",
            "area_ha": 275.8,
            "geometry": Polygon([(18.490, 54.495), (18.520, 54.495), (18.520, 54.520), (18.490, 54.520)]),
        },
        {
            "district_id": "GDY-03",
            "name": "Chylonia",
            "area_ha": 410.2,
            "geometry": Polygon([(18.430, 54.520), (18.490, 54.520), (18.490, 54.555), (18.430, 54.555)]),
        },
        {
            "district_id": "GDY-04",
            "name": "Cisowa",
            "area_ha": 188.7,
            "geometry": Polygon([(18.470, 54.555), (18.510, 54.555), (18.510, 54.575), (18.470, 54.575)]),
        },
    ]
    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
    log.info("Returning placeholder GeoDataFrame with %d districts", len(gdf))
    return gdf
