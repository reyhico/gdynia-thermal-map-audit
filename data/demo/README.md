# Demo Data

This directory contains **synthetic** datasets for development and CI testing.
All data are entirely fictional and must not be used in published analysis.

## Files

| File | Description | Rows |
|---|---|---|
| `demo_districts.geojson` | 4 simplified fake Gdynia district polygons (EPSG:4326) | 4 features |
| `demo_annotations.csv` | Synthetic manual annotation records | 10 |
| `demo_source_inventory.csv` | Synthetic source inventory records | 5 |
| `demo_layer_catalog.csv` | Synthetic layer catalog records | 5 |
| `demo_fetch_log.csv` | Synthetic fetch log records | 5 |

## Usage

Demo data is used automatically when real data files are not present.
Pipeline commands accept `--demo` flag to force demo mode.

```bash
gta run-pipeline --demo
```

## Coordinates

Districts are centred around Gdynia (approximate centre: 54.52°N, 18.53°E) but
their boundaries are simplified rectangles and do not represent actual administrative units.
