"""Zonal statistics computation."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.geodata.zonal_stats")

_SUPPORTED_STATS = {"mean", "min", "max", "count", "median", "std", "sum", "nodata_fraction"}


def compute_zonal_stats(
    raster_path: Path | str,
    zones_gdf: gpd.GeoDataFrame,
    stats: Sequence[str] = ("mean", "median", "min", "max", "count"),
    band: int = 1,
    nodata_value: float | None = None,
) -> pd.DataFrame:
    """Compute per-zone statistics from a raster.

    Parameters
    ----------
    raster_path:
        Path to the raster file.
    zones_gdf:
        GeoDataFrame whose geometries define the zones.  Must be in the same
        CRS as the raster (or will be reprojected automatically).
    stats:
        Statistics to compute.  Supported: mean, median, min, max, count,
        std, sum, nodata_fraction.
    band:
        1-based raster band index.
    nodata_value:
        Override nodata value (uses raster metadata if *None*).

    Returns
    -------
    DataFrame with one row per zone, columns for each requested statistic,
    plus ``zone_index`` matching the GeoDataFrame index.
    """
    import rasterio
    from rasterio.mask import mask as rio_mask

    raster_path = Path(raster_path)
    unsupported = set(stats) - _SUPPORTED_STATS
    if unsupported:
        raise ValueError(f"Unsupported stats: {unsupported}.  Use: {_SUPPORTED_STATS}")

    rows: list[dict] = []
    with rasterio.open(raster_path) as ds:
        raster_crs = ds.crs
        nd = nodata_value if nodata_value is not None else ds.nodata

        # Reproject zones to raster CRS if needed
        if zones_gdf.crs and raster_crs and zones_gdf.crs.to_epsg() != raster_crs.to_epsg():
            zones_gdf = zones_gdf.to_crs(raster_crs)

        for idx, row in zones_gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                rows.append({"zone_index": idx, **dict.fromkeys(stats)})
                continue
            try:
                out_arr, _ = rio_mask(ds, [geom], crop=True, filled=True)
                values = out_arr[band - 1].astype(float)
                valid = values[values != nd] if nd is not None else values.ravel()

                stat_row: dict = {"zone_index": idx}
                for s in stats:
                    if valid.size == 0:
                        stat_row[s] = None
                    elif s == "mean":
                        stat_row[s] = float(np.nanmean(valid))
                    elif s == "median":
                        stat_row[s] = float(np.nanmedian(valid))
                    elif s == "min":
                        stat_row[s] = float(np.nanmin(valid))
                    elif s == "max":
                        stat_row[s] = float(np.nanmax(valid))
                    elif s == "count":
                        stat_row[s] = int(valid.size)
                    elif s == "std":
                        stat_row[s] = float(np.nanstd(valid))
                    elif s == "sum":
                        stat_row[s] = float(np.nansum(valid))
                    elif s == "nodata_fraction":
                        total = values.size
                        stat_row[s] = float((total - valid.size) / total) if total > 0 else 1.0
                rows.append(stat_row)

            except Exception as exc:
                log.warning("Zonal stats failed for zone %s: %s", idx, exc)
                rows.append({"zone_index": idx, **dict.fromkeys(stats)})

    return pd.DataFrame(rows)
