# Limitations and Uncertainty

This document catalogues the principal limitations affecting Phase 1 results.
Researchers using this codebase or citing derived results must read this section carefully.

---

## 1. Uncertain Public Data Access

The thermal-loss map at termalne.obliview.com is a publicly accessible web platform,
but **the underlying data services may not be intended for programmatic bulk access**.
Key uncertainties:

- **No OGC endpoints may be discoverable**: The platform may serve tiles through a
  proprietary renderer with no public WMS/WMTS/WFS endpoint.
- **API may change without notice**: JavaScript configurations and tile URL templates
  are implementation details subject to change by the platform operator.
- **Rate limiting or IP blocking**: Automated probing may trigger throttling.  The pipeline
  enforces a configurable delay (`GTA_REQUEST_DELAY_S`) between requests to minimise impact.
- **Authentication walls**: Some layers or higher-resolution data may require login.

**Implication**: The pipeline must gracefully handle all three scenarios (A/B/C) because
richer data access cannot be guaranteed.

---

## 2. Incomplete and Heterogeneous Spatial Coverage

Even if raster or vector data are accessible:

- **Coverage gaps**: Not all Gdynia districts may be surveyed.  The aerial thermal survey
  may have been conducted in stages or limited to specific building types.
- **Temporal heterogeneity**: Different parts of the dataset may reflect different survey
  dates, acquisition conditions, or atmospheric corrections.
- **Edge effects**: Buildings near district boundaries may be split across units,
  inflating or deflating counts.

---

## 3. Proxy vs. Direct Thermal Measurement

The thermal-loss map shows **apparent surface temperature** (or a derivative thereof)
derived from aerial infrared imaging.  This is a **proxy** for actual building energy loss:

- Roof-surface temperature is affected by insulation, roof colour, solar exposure, wind,
  and measurement time.
- Façade measurements (if present) are affected by surface material, shading, and orientation.
- Thermal bridging and air infiltration are not directly observable from above.
- Outdoor air temperature and humidity at acquisition time affect all readings.

**Implication**: Indicators derived here reflect *apparent anomaly patterns* and must not
be interpreted as certified energy performance assessments.

---

## 4. Manual Annotation Subjectivity

Scenario C relies on human observers interpreting a web map viewer:

- **Visual judgement**: Annotators assign anomaly scale (1–5) based on colour intensity
  displayed in the browser, which may be affected by monitor calibration and rendering artefacts.
- **Sampling bias**: Stratified random sampling reduces but does not eliminate selection bias.
- **Inter-annotator variability**: Without explicit reliability checks (e.g. Krippendorff's α),
  annotation consistency cannot be quantified.
- **Platform rendering**: Browser zoom level, tile compression artefacts, and legend rendering
  can influence perceived intensity.

---

## 5. Coordinate Accuracy

- **Screen-to-coordinate mapping**: When extracting coordinates from the viewer, pixel-to-CRS
  accuracy depends on the viewer's reported zoom/extent parameters.
- **CRS ambiguity**: JavaScript configs may specify projections informally or incorrectly.
  All geometries are validated with `pyproj` before processing.
- **EPSG:2180 vs EPSG:4326**: All internal processing uses EPSG:2180.  Transformations
  introduce sub-metre rounding errors which are negligible for district-level aggregation
  but may matter at building level.

---

## 6. Legal and Ethical Considerations

- **Terms of Service**: The project does not assume any right to redistribute raw data
  obtained from termalne.obliview.com.  Only derived statistical indicators are published.
- **Privacy**: Thermal images may reveal information about building occupancy patterns.
  No individual building records are published without appropriate aggregation.
- **Attribution**: Any publication must credit the original data source and note that
  the thermal survey was commissioned by the City of Gdynia.

---

## 7. Scope Limitations (Phase 1)

Phase 1 intentionally excludes:

- Socioeconomic data integration (Phase 2 scope)
- 3D urban morphology analysis (Phase 2 optional)
- Façade thermal analysis (optional exploratory only)
- Machine learning modelling (Phase 2 scope)
- Longitudinal / multi-year comparison
