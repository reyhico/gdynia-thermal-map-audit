"""Regular grid generation for spatial analysis."""

from __future__ import annotations

import logging
import math
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

log = logging.getLogger("gdynia_thermal_audit.spatial_units.grid")

BBox = tuple[float, float, float, float]  # (xmin, ymin, xmax, ymax)


def generate_grid(
    bbox: BBox,
    cell_size_m: int,
    epsg: int = 2180,
) -> gpd.GeoDataFrame:
    """Generate a regular square-cell grid within a bounding box.

    Parameters
    ----------
    bbox:
        Bounding box as ``(xmin, ymin, xmax, ymax)`` in the coordinate system
        specified by *epsg*.  For EPSG:2180 (PL-1992) the units are metres.
    cell_size_m:
        Cell width and height in metres (100, 250, or 500 recommended).
    epsg:
        EPSG code for the output CRS.  Default: 2180 (PL-1992, projected).

    Returns
    -------
    GeoDataFrame with columns ``cell_id``, ``row``, ``col``, and ``geometry``
    (square Polygon) in the specified CRS.
    """
    xmin, ymin, xmax, ymax = bbox
    cols = math.ceil((xmax - xmin) / cell_size_m)
    rows = math.ceil((ymax - ymin) / cell_size_m)

    geometries = []
    cell_ids = []
    row_ids = []
    col_ids = []

    for r in range(rows):
        for c in range(cols):
            x0 = xmin + c * cell_size_m
            y0 = ymin + r * cell_size_m
            x1 = x0 + cell_size_m
            y1 = y0 + cell_size_m
            geometries.append(box(x0, y0, x1, y1))
            cell_ids.append(f"GRID-{cell_size_m}m-{r:04d}-{c:04d}")
            row_ids.append(r)
            col_ids.append(c)

    gdf = gpd.GeoDataFrame(
        {"cell_id": cell_ids, "row": row_ids, "col": col_ids, "geometry": geometries},
        crs=f"EPSG:{epsg}",
    )
    log.info(
        "Generated %d grid cells (%d rows × %d cols, %d m) in EPSG:%d",
        len(gdf),
        rows,
        cols,
        cell_size_m,
        epsg,
    )
    return gdf


def clip_grid_to_boundary(
    grid_gdf: gpd.GeoDataFrame,
    boundary_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Clip a grid to keep only cells that intersect a boundary polygon.

    Parameters
    ----------
    grid_gdf:
        Grid GeoDataFrame (output of :func:`generate_grid`).
    boundary_gdf:
        Boundary GeoDataFrame (single or multi-polygon).

    Returns
    -------
    Subset of *grid_gdf* where geometries intersect the boundary union.
    """
    if grid_gdf.crs != boundary_gdf.crs:
        boundary_gdf = boundary_gdf.to_crs(grid_gdf.crs)

    boundary_union = boundary_gdf.geometry.union_all()
    clipped = grid_gdf[grid_gdf.geometry.intersects(boundary_union)].copy()
    log.info("Clipped grid: %d → %d cells", len(grid_gdf), len(clipped))
    return clipped


def export_grid(
    grid_gdf: gpd.GeoDataFrame,
    output_dir: Path,
    cell_size_m: int,
) -> Path:
    """Save the grid to a GeoPackage file.

    Parameters
    ----------
    grid_gdf:
        Grid GeoDataFrame to export.
    output_dir:
        Directory where the GPKG is written.
    cell_size_m:
        Cell size (used in the layer name).

    Returns
    -------
    Path to the saved file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "spatial_units.gpkg"
    layer_name = f"grid_{cell_size_m}m"
    grid_gdf.to_file(out_path, layer=layer_name, driver="GPKG")
    log.info("Grid saved to %s (layer: %s)", out_path, layer_name)
    return out_path
