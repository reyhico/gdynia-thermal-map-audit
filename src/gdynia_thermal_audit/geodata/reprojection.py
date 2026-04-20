"""Reprojection utilities for vectors and rasters."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd

log = logging.getLogger("gdynia_thermal_audit.geodata.reprojection")


def reproject_gdf(gdf: gpd.GeoDataFrame, target_epsg: int) -> gpd.GeoDataFrame:
    """Reproject a GeoDataFrame to the target EPSG.

    Parameters
    ----------
    gdf:
        Input GeoDataFrame.
    target_epsg:
        Target EPSG code as integer.

    Returns
    -------
    GeoDataFrame in target CRS.
    """
    if gdf.crs is None:
        log.warning("GeoDataFrame has no CRS; assuming EPSG:4326 before reprojection")
        gdf = gdf.set_crs(epsg=4326)
    if gdf.crs.to_epsg() == target_epsg:
        return gdf
    log.debug("Reprojecting from %s → EPSG:%d", gdf.crs, target_epsg)
    return gdf.to_crs(epsg=target_epsg)


def reproject_raster(
    input_path: Path | str,
    output_path: Path | str,
    target_epsg: int,
    resampling_method: str = "bilinear",
) -> Path:
    """Reproject a raster to the target CRS.

    Parameters
    ----------
    input_path:
        Source raster file.
    output_path:
        Destination raster file.
    target_epsg:
        Target EPSG code.
    resampling_method:
        Rasterio resampling method name (``'nearest'``, ``'bilinear'``, etc.).

    Returns
    -------
    Path to the reprojected raster.
    """
    import rasterio
    from rasterio.crs import CRS
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    _resampling = {
        "nearest": Resampling.nearest,
        "bilinear": Resampling.bilinear,
        "cubic": Resampling.cubic,
        "lanczos": Resampling.lanczos,
    }
    resamp = _resampling.get(resampling_method, Resampling.bilinear)
    dst_crs = CRS.from_epsg(target_epsg)

    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        meta = src.meta.copy()
        meta.update({"crs": dst_crs, "transform": transform, "width": width, "height": height})

        with rasterio.open(output_path, "w", **meta) as dst:
            for band_idx in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band_idx),
                    destination=rasterio.band(dst, band_idx),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=resamp,
                )

    log.info("Reprojected raster saved to %s", output_path)
    return output_path
