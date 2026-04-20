# Gdynia Thermal Map Audit

> **Phase 1 — Web Map Audit, Asset Discovery, Analytical Database & Thermal Indicators**

[![CI](https://github.com/reyhico/gdynia-thermal-map-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/reyhico/gdynia-thermal-map-audit/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg)](LICENSE)

---

## Overview

This repository contains a reproducible, research-grade Python pipeline for auditing
the public thermal-loss web map of Gdynia, Poland
([termalne.obliview.com](https://termalne.obliview.com)).

The study is **methodological**: it develops and demonstrates a workflow for systematically
characterising what thermal data are publicly available and deriving spatial indicators of
building thermal-loss anomalies at the district, neighbourhood, and grid-cell level.

### Research Questions

1. What data assets are publicly accessible from the Gdynia thermal platform?
2. What OGC services (WMS/WMTS/WFS) or file downloads can be discovered via web audit?
3. What spatial patterns of thermal-loss anomalies can be quantified from available data?
4. How do indicators vary across spatial unit types (districts vs. neighbourhoods vs. grid)?

---

## Why Phase 1 Only?

Phase 1 focuses exclusively on the **supply side** (what data exist and how they are served)
and on **descriptive spatial indicators**.  It deliberately **excludes**:

- Socioeconomic covariate integration (planned Phase 2)
- Machine learning modelling (planned Phase 2)
- 3D urban morphology analysis (optional Phase 2 extension)
- Façade thermal analysis (optional exploratory extension)

Phase 1 is designed to be publishable as a standalone methodological contribution regardless
of how much machine-readable data proves to be publicly accessible from the target platform.
See `docs/phase2_outlook.md` for Phase 2 plans.

---

## Analytical Stance

- **2D-first**: All analysis is planar (EPSG:2180, PL-1992 national grid).  3D extensions
  are optional hooks only.
- **Scenario-agnostic**: The pipeline supports three scenarios depending on data availability
  (see [Scenarios](#scenarios-raster--vector--annotation)).
- **Spatial units — districts first**: The preferred aggregation unit is Gdynia's 18
  administrative districts, then sub-district neighbourhoods, then a regular grid
  (100 / 250 / 500 m) as fallback.

---

## Installation

### Prerequisites

- Python 3.10 or later
- GDAL system library (for rasterio/geopandas)

```bash
# Ubuntu / Debian
sudo apt-get install libgdal-dev gdal-bin libspatialindex-dev

# macOS (Homebrew)
brew install gdal spatialindex
```

### Install

```bash
git clone https://github.com/reyhico/gdynia-thermal-map-audit.git
cd gdynia-thermal-map-audit

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install the package with dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (optional but recommended)
pre-commit install
```

### Configure

```bash
cp .env.example .env
# Edit .env with your settings (optional; defaults work for demo mode)
```

---

## First Commands

```bash
# Run the full demo pipeline (uses synthetic data, no network access)
gta run-pipeline --demo

# Or step by step:
gta audit-site                    # Download and parse the landing page
gta probe-endpoints               # Probe discovered OGC endpoints
gta build-grid --size 250         # Generate 250 m analysis grid
gta compute-annotation-indicators # Compute Scenario C indicators from annotations
gta export-article-tables         # Export CSV + LaTeX tables
```

```bash
# Help for any command
gta --help
gta build-grid --help
```

---

## Scenarios: Raster / Vector / Annotation

The pipeline adapts to whatever data are publicly accessible:

| Scenario | Data source | Key indicators | Status |
|---|---|---|---|
| **A — Raster** | WMS/WMTS tile download or GeoTIFF | `coverage_ratio`, `mean_intensity`, `anomalous_area_share` | Attempted first (auto mode) |
| **B — Vector** | WFS/GeoJSON feature download | `anomaly_count`, `anomaly_density_per_ha`, `building_anomaly_share` | Attempted second |
| **C — Annotation** | Manual annotation CSV | Same as B, plus `anomaly_scale_1_5` | Always available as fallback |

Set `scenario: auto` in `config/config.example.yaml` (or `--scenario` CLI flag) to let the
pipeline select automatically.  The `data_source` column in output CSVs records which
scenario was used.

---

## Spatial Units

Three aggregation levels are supported:

| Level | Config key | Fallback |
|---|---|---|
| Districts (18 units) | `spatial_units.preferred: districts` | Placeholder polygons in `spatial_units/districts.py` |
| Neighbourhoods | `spatial_units.preferred: neighborhoods` | Requires external file |
| Regular grid | `build-grid --size 250` | Always available |

Import official boundaries:

```bash
gta import-districts data/external/gdynia_districts.geojson
gta import-neighborhoods data/external/gdynia_neighborhoods.geojson
```

---

## Manual Annotation

When machine-readable data are unavailable, the Scenario C workflow enables
systematic human annotation of the web viewer:

```bash
# Create the annotation template
gta inventory-assets --create-annotation-template
# → data/annotations/annotation_template.csv

# Validate completed annotations
gta validate-annotations data/annotations/annotations.csv

# Merge multiple annotation batches
gta merge-annotations data/annotations/existing.csv data/annotations/new_batch.csv
```

See `docs/manual_annotation.md` for the full protocol.

---

## Feasible Outputs Under Different Data Availability Conditions

| Data available | Publishable outputs |
|---|---|
| Full raster (Scenario A) | Choropleth maps of mean/median intensity; anomalous area share; priority index with all components |
| Vector features (Scenario B) | Anomaly density maps; building anomaly share; priority index without raster components |
| Annotation only (Scenario C) | Descriptive statistics of annotated buildings; district rankings by annotation-based priority index |
| No data accessible | Methodological paper: audit workflow documentation + limitations analysis |

All four outcomes are publishable contributions at the methodological level.

---

## Project Structure

```
gdynia-thermal-map-audit/
├── config/                  # Config and logging YAML
├── data/
│   ├── raw/                 # Downloaded HTML, JS, XML (gitignored)
│   ├── interim/             # Parsed inventories (gitignored)
│   ├── processed/           # Indicators, GeoPackages (gitignored)
│   ├── annotations/         # Manual annotation CSV (gitignored)
│   └── demo/                # Synthetic demo data (committed)
├── docs/                    # Methodology, indicator dictionary, etc.
├── notebooks/               # Jupyter notebooks (01–07)
├── outputs/
│   ├── tables/              # CSV and LaTeX tables
│   ├── figures/             # Choropleth maps and plots
│   └── logs/                # Run logs (gitignored)
├── src/gdynia_thermal_audit/
│   ├── cli.py               # Typer CLI entry point
│   ├── settings.py          # Pydantic settings (env vars)
│   ├── frontend_audit/      # HTML audit, JS config parsing
│   ├── network_probe/       # HTTP probing, OGC capabilities
│   ├── downloader/          # File download with retry / checksums
│   ├── parser/              # JS config and URL extraction
│   ├── geodata/             # CRS, raster, vector, zonal stats
│   ├── spatial_units/       # Districts, neighbourhoods, grid
│   ├── indicators/          # Raster, vector, annotation indicators
│   ├── annotation/          # Templates, validation, merge
│   ├── reporting/           # Tables, figures, LaTeX export
│   ├── schemas/             # Pydantic v2 data models
│   └── utils/               # IO, hashing, text, time
└── tests/                   # pytest test suite
```

---

## Development

```bash
make lint          # ruff check + format check
make format        # ruff format + fix
make test          # pytest
make test-cov      # pytest with HTML coverage report
make clean         # remove __pycache__, build artefacts
```

---

## Legal and Ethical Considerations

- The thermal-loss platform at termalne.obliview.com is a **public** web service operated
  by or on behalf of the City of Gdynia.
- This project performs **polite, rate-limited** HTTP requests only (default delay 1 s).
- **No raw data** obtained from the platform are redistributed in this repository.
  Only derived statistical indicators are published.
- Any publication must credit the original data source and the City of Gdynia.
- The survey underlying the platform was commissioned by the City; conditions of use
  should be verified before publication.

See `docs/limitations.md` for a full discussion of limitations and uncertainties.

---

## Reproducibility

Every pipeline run produces a `PipelineRunLog` JSON record in `outputs/logs/`.
See `docs/reproducibility.md` for full provenance documentation and rerun instructions.

---

## Citation

If you use this code or methodology, please cite:

```
Gdynia Thermal Map Audit — Phase 1 research package (v0.1.0)
https://github.com/reyhico/gdynia-thermal-map-audit
```

---

## Licence

Code: [CC0-1.0](LICENSE) — public domain dedication.

Demo data (`data/demo/`) is entirely synthetic and carries no copyright.