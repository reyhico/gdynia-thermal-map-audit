# Indicator Dictionary

This document defines all thermal-loss indicators computed by the pipeline.
Each indicator is described with its formula, data source(s), and known caveats.

---

## Notation

| Symbol | Meaning |
|---|---|
| *Z* | A spatial unit (district, neighbourhood, or grid cell) |
| *A(Z)* | Total area of *Z* in hectares |
| *P_r(Z)* | Pixels with valid (non-nodata) raster coverage within *Z* |
| *P_t(Z)* | Total pixels within *Z* (extent) |
| *v(p)* | Normalised intensity value of pixel *p* ∈ [0, 1] |
| *τ* | Anomaly threshold (default 0.75, configurable) |
| *F* | Set of discrete anomaly features (points or polygons) within *Z* |
| *B(Z)* | Set of buildings intersecting *Z* |

---

## Indicators

### 1. `coverage_ratio`

**Definition**: Fraction of the spatial unit covered by valid raster data.

**Formula**:

```
coverage_ratio(Z) = |P_r(Z)| / |P_t(Z)|
```

**Data source**: Raster (Scenario A)

**Caveats**: Low values indicate sparse data; zones with `coverage_ratio < 0.10` are flagged
and excluded from intensity statistics by default.

---

### 2. `anomaly_count`

**Definition**: Count of discrete anomaly features (points or polygon centroids) falling
within the spatial unit.

**Formula**:

```
anomaly_count(Z) = |F ∩ Z|
```

**Data source**: Vector (Scenario B) or Annotation (Scenario C)

**Caveats**: Depends entirely on how the source platform defines "anomaly".  Double-counting
may occur if features overlap unit boundaries.

---

### 3. `anomaly_density_per_ha`

**Definition**: Anomaly count per hectare of the spatial unit.

**Formula**:

```
anomaly_density_per_ha(Z) = anomaly_count(Z) / A(Z)
```

**Data source**: Vector (Scenario B) or Annotation (Scenario C)

**Caveats**: Sensitive to unit size.  Small units (< 1 ha) can yield inflated densities.

---

### 4. `mean_intensity`

**Definition**: Mean normalised thermal-loss intensity across all valid pixels within *Z*.

**Formula**:

```
mean_intensity(Z) = mean{ v(p) : p ∈ P_r(Z) }
```

**Data source**: Raster (Scenario A)

**Caveats**: Normalisation method affects comparability across runs.  See `anomaly_threshold`
config parameter.

---

### 5. `median_intensity`

**Definition**: Median normalised intensity within *Z*.

**Formula**: 50th percentile of *{v(p) : p ∈ P_r(Z)}*

**Data source**: Raster (Scenario A)

**Caveats**: More robust than mean to outlier pixels but less sensitive to high-intensity tails.

---

### 6. `anomalous_area_share`

**Definition**: Fraction of valid pixels classified as anomalous (above threshold *τ*).

**Formula**:

```
anomalous_area_share(Z) = |{p ∈ P_r(Z) : v(p) ≥ τ}| / |P_r(Z)|
```

**Data source**: Raster (Scenario A)

**Caveats**: Binary threshold introduces hard classification boundary.  Sensitivity analysis
across *τ* values is recommended.

---

### 7. `building_anomaly_count`

**Definition**: Number of buildings within *Z* that intersect at least one anomaly feature
(vector) or have `observed_anomaly = True` in annotations.

**Formula**:

```
building_anomaly_count(Z) = |{b ∈ B(Z) : b ∩ F ≠ ∅}|
```

**Data source**: Vector (Scenario B) or Annotation (Scenario C)

**Caveats**: Requires a building footprint layer.  If unavailable, this indicator is null.

---

### 8. `building_anomaly_share`

**Definition**: Fraction of buildings within *Z* that have a detected anomaly.

**Formula**:

```
building_anomaly_share(Z) = building_anomaly_count(Z) / |B(Z)|
```

**Data source**: Vector (Scenario B) or Annotation (Scenario C)

**Caveats**: Denominator is the count of buildings intersecting the unit, not all buildings
in Gdynia.  Building footprint completeness directly affects this indicator.

---

### 9. `priority_index`

**Definition**: Composite normalised index combining multiple indicators into a single
priority score for spatial unit ranking.

**Formula**:

The index is computed as a weighted sum of z-score standardised component indicators:

```
priority_index(Z) = Σ_i  w_i · z_i(Z)
```

where *z_i* is the z-score of indicator *i* across all units, and *w_i* is the configured
weight (default: equal weights).

**Default components** (configurable via `weights` dict):

| Component | Default weight |
|---|---|
| `anomalous_area_share` | 0.30 |
| `anomaly_density_per_ha` | 0.25 |
| `building_anomaly_share` | 0.25 |
| `mean_intensity` | 0.20 |

**Data source**: Composite (uses whatever indicators are available given the scenario)

**Caveats**:
- Missing component indicators are imputed with the unit mean before standardisation.
- Equal weighting is a simplification; domain-expert weighting is recommended for publication.
- The index is relative: it ranks units against each other, not against an absolute standard.

---

## Scenario–Indicator Availability Matrix

| Indicator | Scenario A (Raster) | Scenario B (Vector) | Scenario C (Annotation) |
|---|---|---|---|
| `coverage_ratio` | ✓ | — | — |
| `anomaly_count` | — | ✓ | ✓ |
| `anomaly_density_per_ha` | — | ✓ | ✓ |
| `mean_intensity` | ✓ | — | — |
| `median_intensity` | ✓ | — | — |
| `anomalous_area_share` | ✓ | — | — |
| `building_anomaly_count` | — | ✓ | ✓ |
| `building_anomaly_share` | — | ✓ | ✓ |
| `priority_index` | ✓ (partial) | ✓ (partial) | ✓ (partial) |
