"""Tests for raster_utils using a synthetic in-memory raster."""

from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from gdynia_thermal_audit.geodata.raster_utils import compute_raster_stats, read_raster_metadata


@pytest.fixture
def synthetic_raster(tmp_path: Path) -> Path:
    """Write a tiny 10×10 GeoTIFF to a temp file and return its path."""
    raster_path = tmp_path / "test_thermal.tif"
    width, height = 10, 10

    # Values from 0.0 to 1.0
    data = np.linspace(0.0, 1.0, width * height, dtype=np.float32).reshape(1, height, width)

    transform = from_bounds(18.40, 54.44, 18.50, 54.52, width, height)
    crs = CRS.from_epsg(4326)

    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        crs=crs,
        transform=transform,
        nodata=-9999.0,
    ) as ds:
        ds.write(data)

    return raster_path


@pytest.fixture
def raster_with_nodata(tmp_path: Path) -> Path:
    """Write a 5×5 raster where half the pixels are nodata."""
    raster_path = tmp_path / "test_nodata.tif"
    width, height = 5, 5
    nodata = -9999.0
    data = np.ones((1, height, width), dtype=np.float32)
    # Set top half to nodata
    data[0, :2, :] = nodata

    transform = from_bounds(18.40, 54.44, 18.50, 54.52, width, height)

    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        crs=CRS.from_epsg(4326),
        transform=transform,
        nodata=nodata,
    ) as ds:
        ds.write(data)

    return raster_path


class TestReadRasterMetadata:
    def test_returns_dict(self, synthetic_raster):
        meta = read_raster_metadata(synthetic_raster)
        assert isinstance(meta, dict)

    def test_width_height(self, synthetic_raster):
        meta = read_raster_metadata(synthetic_raster)
        assert meta["width"] == 10
        assert meta["height"] == 10

    def test_crs(self, synthetic_raster):
        meta = read_raster_metadata(synthetic_raster)
        assert meta["epsg"] == 4326

    def test_band_count(self, synthetic_raster):
        meta = read_raster_metadata(synthetic_raster)
        assert meta["count"] == 1

    def test_bbox_wgs84(self, synthetic_raster):
        meta = read_raster_metadata(synthetic_raster)
        bbox = meta["bbox_wgs84"]
        assert bbox is not None
        assert len(bbox) == 4
        # Should be approx [18.40, 54.44, 18.50, 54.52]
        assert abs(bbox[0] - 18.40) < 0.01
        assert abs(bbox[2] - 18.50) < 0.01


class TestComputeRasterStats:
    def test_returns_dict(self, synthetic_raster):
        stats = compute_raster_stats(synthetic_raster)
        assert isinstance(stats, dict)

    def test_min_max(self, synthetic_raster):
        stats = compute_raster_stats(synthetic_raster)
        assert stats["min"] == pytest.approx(0.0, abs=0.01)
        assert stats["max"] == pytest.approx(1.0, abs=0.01)

    def test_valid_pixel_count(self, synthetic_raster):
        stats = compute_raster_stats(synthetic_raster)
        assert stats["valid_pixels"] == 100  # 10 × 10

    def test_nodata_fraction(self, raster_with_nodata):
        stats = compute_raster_stats(raster_with_nodata)
        # 2 out of 5 rows set to nodata → 10 / 25 nodata pixels
        assert stats["nodata_fraction"] == pytest.approx(10 / 25, rel=0.01)

    def test_mean_is_sensible(self, synthetic_raster):
        stats = compute_raster_stats(synthetic_raster)
        assert 0.0 < stats["mean"] < 1.0
