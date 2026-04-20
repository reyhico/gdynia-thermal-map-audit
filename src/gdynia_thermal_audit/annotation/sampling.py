"""Building sampling for annotation campaigns."""

from __future__ import annotations

import logging
from typing import Literal, Optional

import geopandas as gpd
import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.annotation.sampling")


def sample_buildings(
    buildings_gdf: gpd.GeoDataFrame,
    n: int,
    method: Literal["random", "stratified"] = "random",
    spatial_unit_gdf: Optional[gpd.GeoDataFrame] = None,
    random_state: int = 42,
) -> gpd.GeoDataFrame:
    """Sample buildings for manual annotation.

    Parameters
    ----------
    buildings_gdf:
        GeoDataFrame of building footprints.
    n:
        Target total sample size.
    method:
        ``'random'`` — simple random sample.
        ``'stratified'`` — proportional stratified sample by spatial unit
        (requires *spatial_unit_gdf*).
    spatial_unit_gdf:
        Spatial unit GeoDataFrame used for stratification.  Required when
        *method* is ``'stratified'``.
    random_state:
        Random seed for reproducibility.

    Returns
    -------
    Sampled GeoDataFrame with an added ``_sample_weight`` column indicating
    the inverse sampling probability.
    """
    if len(buildings_gdf) == 0:
        log.warning("Empty buildings GeoDataFrame; returning empty sample")
        return buildings_gdf.copy()

    n = min(n, len(buildings_gdf))

    if method == "random":
        sampled = buildings_gdf.sample(n=n, random_state=random_state).copy()
        sampled["_sample_weight"] = len(buildings_gdf) / n
        return sampled

    if method == "stratified":
        if spatial_unit_gdf is None:
            raise ValueError("spatial_unit_gdf must be provided for stratified sampling")

        # Spatial join to assign each building to a unit
        if buildings_gdf.crs != spatial_unit_gdf.crs:
            spatial_unit_gdf = spatial_unit_gdf.to_crs(buildings_gdf.crs)

        joined = gpd.sjoin(buildings_gdf, spatial_unit_gdf[["geometry"]], how="left", predicate="intersects")
        unit_col = "index_right"

        unit_counts = joined[unit_col].value_counts()
        total_buildings = len(joined)
        samples: list[gpd.GeoDataFrame] = []

        for unit_id, count in unit_counts.items():
            proportion = count / total_buildings
            unit_n = max(1, round(n * proportion))
            unit_buildings = joined[joined[unit_col] == unit_id]
            unit_sample = unit_buildings.sample(
                n=min(unit_n, len(unit_buildings)), random_state=random_state
            ).copy()
            unit_sample["_sample_weight"] = count / len(unit_sample)
            samples.append(unit_sample)

        if not samples:
            return buildings_gdf.iloc[:0].copy()

        result = pd.concat(samples)
        # Drop the join column
        if unit_col in result.columns:
            result = result.drop(columns=[unit_col])
        return gpd.GeoDataFrame(result, crs=buildings_gdf.crs)

    raise ValueError(f"Unknown sampling method: '{method}'")
