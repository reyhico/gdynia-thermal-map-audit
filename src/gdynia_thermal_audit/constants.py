"""Project-wide constants."""

from pathlib import Path

EPSG_POLAND: int = 2180
EPSG_WGS84: int = 4326

TARGET_LANDING_URL: str = "https://termalne.obliview.com"
GRID_SIZES_M: list[int] = [100, 250, 500]
DEFAULT_REQUEST_DELAY_S: float = 1.0
DEFAULT_USER_AGENT: str = "GdyniaThermalAudit/0.1 (academic research)"

# Approximate WGS-84 bounding box for Gdynia municipality
# (min_lon, min_lat, max_lon, max_lat)
GDYNIA_BBOX_WGS84: tuple[float, float, float, float] = (18.38, 54.42, 18.65, 54.60)

# Anomaly threshold (normalised intensity, 0–1)
DEFAULT_ANOMALY_THRESHOLD: float = 0.75

# Minimum coverage ratio for a spatial unit to be included in raster stats
MIN_COVERAGE_RATIO: float = 0.10

# Annotation scale bounds
ANOMALY_SCALE_MIN: int = 1
ANOMALY_SCALE_MAX: int = 5

VISIBILITY_QUALITY_MIN: int = 1
VISIBILITY_QUALITY_MAX: int = 3

# Data directory names
RAW_SUBDIR = "raw"
INTERIM_SUBDIR = "interim"
PROCESSED_SUBDIR = "processed"
EXTERNAL_SUBDIR = "external"
ANNOTATIONS_SUBDIR = "annotations"
