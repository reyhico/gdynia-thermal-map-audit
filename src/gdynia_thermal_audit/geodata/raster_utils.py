"""Raster utility functions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

log = logging.getLogger("gdynia_thermal_audit.geodata.raster_utils")


def read_raster_metadata(path: Path | str) -> dict[str, Any]:
    """Read metadata from a raster file without loading the pixel data.

    Parameters
    ----------
    path:
        Path to the raster file (GeoTIFF or compatible format).

    Returns
    -------
    Dict with keys: ``crs``, ``width``, ``height``, ``count`` (bands),
    ``dtype``, ``nodata``, ``transform``, ``bounds``, ``bbox_wgs84``.
    """
    import rasterio
    from pyproj import Transformer

    path = Path(path)
    with rasterio.open(path) as ds:
        crs = ds.crs
        bounds = ds.bounds
        meta: dict[str, Any] = {
            "path": str(path),
            "crs": str(crs) if crs else None,
            "epsg": crs.to_epsg() if crs else None,
            "width": ds.width,
            "height": ds.height,
            "count": ds.count,
            "dtype": str(ds.dtypes[0]),
            "nodata": ds.nodata,
            "transform": list(ds.transform)[:6],
            "bounds": {
                "left": bounds.left,
                "bottom": bounds.bottom,
                "right": bounds.right,
                "top": bounds.top,
            },
        }

        # Compute WGS-84 bounding box
        try:
            if crs and crs.to_epsg() != 4326:
                transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
                lon_min, lat_min = transformer.transform(bounds.left, bounds.bottom)
                lon_max, lat_max = transformer.transform(bounds.right, bounds.top)
            else:
                lon_min, lat_min = bounds.left, bounds.bottom
                lon_max, lat_max = bounds.right, bounds.top
            meta["bbox_wgs84"] = [lon_min, lat_min, lon_max, lat_max]
        except Exception as exc:
            log.warning("Could not compute WGS-84 bbox: %s", exc)
            meta["bbox_wgs84"] = None

    return meta


def compute_raster_stats(path: Path | str, band: int = 1) -> dict[str, Any]:
    """Compute basic statistics for a raster band.

    Parameters
    ----------
    path:
        Path to the raster file.
    band:
        1-based band index.

    Returns
    -------
    Dict with keys: ``min``, ``max``, ``mean``, ``std``, ``median``,
    ``nodata_fraction``, ``valid_pixels``, ``total_pixels``.
    """
    import rasterio

    with rasterio.open(path) as ds:
        arr = ds.read(band).astype(float)
        nodata = ds.nodata

    total = arr.size
    if nodata is not None:
        mask = arr == nodata
        valid = arr[~mask]
    else:
        valid = arr.ravel()

    if valid.size == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "median": None,
            "nodata_fraction": 1.0,
            "valid_pixels": 0,
            "total_pixels": total,
        }

    return {
        "min": float(np.nanmin(valid)),
        "max": float(np.nanmax(valid)),
        "mean": float(np.nanmean(valid)),
        "std": float(np.nanstd(valid)),
        "median": float(np.nanmedian(valid)),
        "nodata_fraction": float((total - valid.size) / total),
        "valid_pixels": int(valid.size),
        "total_pixels": int(total),
    }


def clip_raster_to_polygon(
    raster_path: Path | str,
    polygon: Any,
    output_path: Path | str,
) -> Path:
    """Clip a raster to a shapely polygon and save the result.

    Parameters
    ----------
    raster_path:
        Source raster file.
    polygon:
        Shapely geometry to use as the clip mask.
    output_path:
        Destination file path.

    Returns
    -------
    Path to the output raster.
    """
    import rasterio
    from rasterio.mask import mask as rio_mask

    raster_path = Path(raster_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(raster_path) as src:
        out_image, out_transform = rio_mask(src, [polygon], crop=True)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )
        with rasterio.open(output_path, "w", **out_meta) as dst:
            dst.write(out_image)

    return output_path
