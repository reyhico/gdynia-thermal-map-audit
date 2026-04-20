"""Tests for spatial grid generation."""

import geopandas as gpd
import pytest
from shapely.geometry import box

from gdynia_thermal_audit.spatial_units.grid import (
    clip_grid_to_boundary,
    generate_grid,
)

# Small test bbox in EPSG:2180 coordinates (metres)
_BBOX = (500_000.0, 500_000.0, 500_500.0, 500_500.0)  # 500 m × 500 m area


def test_generate_grid_cell_count():
    """Grid should produce the expected number of cells."""
    gdf = generate_grid(_BBOX, cell_size_m=100, epsg=2180)
    # 500m / 100m = 5 rows × 5 cols = 25 cells
    assert len(gdf) == 25


def test_generate_grid_cell_count_250m():
    bbox = (0.0, 0.0, 1000.0, 1000.0)
    gdf = generate_grid(bbox, cell_size_m=250)
    # ceil(1000/250) = 4 rows × 4 cols = 16 cells
    assert len(gdf) == 16


def test_generate_grid_crs():
    gdf = generate_grid(_BBOX, cell_size_m=100, epsg=2180)
    assert gdf.crs is not None
    assert gdf.crs.to_epsg() == 2180


def test_generate_grid_cells_are_squares():
    """Each cell should be a square with the expected side length."""
    cell_size = 250
    bbox = (0.0, 0.0, 1000.0, 1000.0)
    gdf = generate_grid(bbox, cell_size_m=cell_size)

    for _, row in gdf.iterrows():
        geom = row.geometry
        minx, miny, maxx, maxy = geom.bounds
        width = round(maxx - minx, 6)
        height = round(maxy - miny, 6)
        assert width == pytest.approx(cell_size, rel=1e-6), f"Cell width mismatch: {width}"
        assert height == pytest.approx(cell_size, rel=1e-6), f"Cell height mismatch: {height}"


def test_generate_grid_has_cell_id():
    gdf = generate_grid(_BBOX, cell_size_m=100)
    assert "cell_id" in gdf.columns
    assert gdf["cell_id"].notna().all()


def test_clip_grid_to_boundary():
    """Clipping should reduce the cell count."""
    gdf_grid = generate_grid((0.0, 0.0, 1000.0, 1000.0), cell_size_m=100)

    # Boundary covers only the bottom-left quarter
    boundary = gpd.GeoDataFrame(
        {"geometry": [box(0.0, 0.0, 500.0, 500.0)]},
        crs="EPSG:2180",
    )
    clipped = clip_grid_to_boundary(gdf_grid, boundary)
    assert len(clipped) < len(gdf_grid)
    assert len(clipped) > 0


def test_generate_grid_no_overlap():
    """Consecutive cells in the same row should not overlap."""
    gdf = generate_grid((0.0, 0.0, 300.0, 100.0), cell_size_m=100)
    cells = list(gdf.geometry)
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            intersection = cells[i].intersection(cells[j])
            assert intersection.area == pytest.approx(0.0, abs=1e-6), (
                f"Cells {i} and {j} overlap with area {intersection.area}"
            )


def test_generate_grid_500m():
    bbox = (0.0, 0.0, 2000.0, 2000.0)
    gdf = generate_grid(bbox, cell_size_m=500)
    assert len(gdf) == 16  # 4 × 4
