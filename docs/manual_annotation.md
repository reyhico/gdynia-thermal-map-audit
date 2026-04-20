# Manual Annotation Protocol

This document describes the protocol for collecting manual thermal-loss observations
from the web viewer at termalne.obliview.com.  It is used in Scenario C (annotation-based
indicators) and as a quality check for Scenarios A and B.

---

## 1. Purpose and Scope

Manual annotation creates a structured, reproducible sample of human-interpreted
thermal-loss observations.  It is the primary data source when machine-readable
layers cannot be accessed, and a validation layer when they can.

---

## 2. Sampling Strategy

### 2.1 Unit of Observation

The unit of observation is a **building** visible in the web viewer.

### 2.2 Sampling Frame

The sampling frame is constructed from one of:
1. Official building footprints (BDOT10k, OSM) intersected with Gdynia's boundary.
2. A regular grid of viewer screenshots (if footprints are unavailable).

### 2.3 Sample Size

A minimum of **n = 30 buildings per district** is recommended for district-level
indicator computation.  For exploratory analysis, a pilot sample of 10 buildings
per district is sufficient.

### 2.4 Sampling Method

Use the `sample_buildings` function (`annotation/sampling.py`) with `method='stratified'`
to draw proportional samples from each district.  Random seed must be recorded for
reproducibility.

### 2.5 Fallback: Convenience Sample

If building footprints are unavailable, annotators select buildings by inspecting the viewer
systematically from NW to SE, recording every *k*-th visible building.  Document the
step value *k* in the `notes` field.

---

## 3. Annotation Protocol

### 3.1 Preparation

1. Open the viewer at the URL recorded in `GTA_VIEWER_URL`.
2. Set zoom level to see individual buildings clearly (typically zoom 17–18).
3. Open the annotation CSV (`data/annotations/annotations.csv`) in a spreadsheet editor.
4. Copy the `record_id` scheme from the template (format: `ANN-{YYYYMMDD}-{seq:04d}`).

### 3.2 Per-Building Steps

For each sampled building:

1. Navigate to the building in the viewer.
2. Record `lon` and `lat` from the viewer's coordinate display (WGS 84 decimal degrees).
3. Record `address` if displayed; otherwise leave blank.
4. Assign `district` and `neighborhood` from the sampling frame.
5. Record `source_url` (full URL including zoom/lat/lon parameters if present).
6. Take a screenshot; save as `data/annotations/screenshots/{record_id}.png`; record
   filename in `screenshot_ref`.
7. Assess `observed_anomaly` (True/False): is there a visible warm-colour area on the
   building's roof or façade?
8. If `observed_anomaly = True`:
   - Assign `anomaly_scale_1_5` (1 = faint, 5 = intense), guided by the legend.
   - Estimate `apparent_area_m2` by comparison with the scale bar.
   - Set `roof_flag` / `facade_flag` / `network_adjacent_flag` as appropriate.
9. Assign `visibility_quality` (1–3): 1 = clear, 2 = partially obscured, 3 = poor.
10. Enter `annotator` initials and `annotation_date` (ISO 8601: YYYY-MM-DD).

### 3.3 Inter-Annotator Consistency Check

At least **10 %** of records should be independently re-annotated by a second annotator.
Disagreements in `anomaly_scale_1_5` greater than ±1 are flagged for review.

---

## 4. Annotation CSV Template Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `record_id` | string | ✓ | Unique ID (e.g. `ANN-20240601-0001`) |
| `building_id` | string | | External building ID (OSM / BDOT) |
| `lon` | float | ✓ | Longitude (WGS 84) |
| `lat` | float | ✓ | Latitude (WGS 84) |
| `address` | string | | Street address if visible |
| `district` | string | | Gdynia district name |
| `neighborhood` | string | | Sub-district neighborhood |
| `spatial_unit_id` | string | | Linked spatial unit ID |
| `source_url` | string | ✓ | Viewer URL at time of observation |
| `screenshot_ref` | string | | Filename of screenshot |
| `observed_anomaly` | boolean | ✓ | True if thermal anomaly observed |
| `anomaly_scale_1_5` | int (1–5) | | Visual intensity scale (if anomaly) |
| `apparent_area_m2` | float | | Estimated anomalous area |
| `roof_flag` | boolean | | Anomaly on roof |
| `facade_flag` | boolean | | Anomaly on façade |
| `network_adjacent_flag` | boolean | | Near district heating network |
| `visibility_quality` | int (1–3) | ✓ | Viewing quality |
| `annotator` | string | ✓ | Annotator initials |
| `annotation_date` | date | ✓ | ISO 8601 date |
| `notes` | string | | Free text |

---

## 5. Uncertainty Documentation

Each record with `anomaly_scale_1_5` should also have `visibility_quality` ≤ 2.
Records with `visibility_quality = 3` are retained but flagged as low-confidence and
excluded from primary statistical summaries.

Uncertainty sources to document in `notes`:
- Tile loading failures (blank areas)
- Shadow or occlusion artefacts
- Ambiguous legend colour mapping
- Very small building footprint

---

## 6. Generating the Blank Template

```bash
gta inventory-assets --create-annotation-template
# or
python -c "from gdynia_thermal_audit.annotation.templates import create_annotation_csv; create_annotation_csv('data/annotations/annotations.csv', n_rows=0)"
```
