# Article Outline

Proposed structure for the peer-reviewed paper arising from this study.

---

## Provisional Title

**"Auditing Public Thermal-Loss Web Maps: A Geospatial Methodology for Urban Energy
Anomaly Detection — A Case Study of Gdynia, Poland"**

---

## Abstract (target ~250 words)

- Context: urban energy efficiency; role of thermal imaging in policy
- Gap: no systematic methodology for auditing publicly deployed thermal-loss web maps
- Contribution: reproducible audit + indicator framework
- Study area: Gdynia (pop. ~250k), Poland
- Method summary: web audit → OGC service discovery → spatial indicator computation
- Key results: (scenario-dependent; placeholder)
- Conclusions: methodological contribution; policy implications

---

## 1. Introduction

1.1 Urban energy challenges and building thermal performance
1.2 Emergence of public thermal-loss web maps
1.3 Research gap: lack of systematic audit methodology
1.4 Study aim and research questions:
   - RQ1: What data are publicly accessible from the Gdynia thermal platform?
   - RQ2: What spatial patterns of thermal-loss anomalies can be derived?
   - RQ3: How do indicators vary across spatial unit types?
1.5 Paper structure

---

## 2. Study Area

2.1 Gdynia: geographic, demographic, and urban context
2.2 Building stock characteristics and heating infrastructure
2.3 The Gdynia thermal-loss mapping initiative
2.4 Spatial units used: districts, neighborhoods, grid

---

## 3. Data and Methods

### 3.1 Web Audit Methodology

3.1.1 Platform discovery and HTML parsing
3.1.2 JavaScript configuration extraction
3.1.3 Network endpoint probing
3.1.4 OGC capabilities enumeration
3.1.5 Asset inventory and provenance logging

### 3.2 Spatial Units

3.2.1 Administrative districts (18 units)
3.2.2 Neighborhoods (sub-district level)
3.2.3 Regular grid (100 / 250 / 500 m)

### 3.3 Indicator Framework

3.3.1 Raster-based indicators (Scenario A)
3.3.2 Vector-based indicators (Scenario B)
3.3.3 Annotation-based indicators (Scenario C)
3.3.4 Priority index computation

### 3.4 Manual Annotation Protocol

3.4.1 Sampling strategy
3.4.2 Observation protocol
3.4.3 Inter-annotator reliability

---

## 4. Results

*Note: content depends on which scenario is applicable.*

### 4.1 Audit Findings

Table 1: Source inventory summary
Table 2: Discovered layers and services

### 4.2 Spatial Indicator Results

Figure 1: Choropleth map — priority index by district
Figure 2: Choropleth map — mean intensity / anomaly density
Table 3: District-level indicator summary statistics
Table 4: Scenario comparison (where multiple scenarios available)

### 4.3 Scenario-Dependent Results

4.3.1 If Scenario A (raster): raster coverage, intensity distribution
4.3.2 If Scenario B (vector): feature counts, density maps
4.3.3 Scenario C: annotation statistics, inter-annotator consistency

---

## 5. Discussion

5.1 Methodological contribution: reproducible open-source audit framework
5.2 Comparison of indicator sets across scenarios
5.3 Policy implications: which districts are high-priority?
5.4 Limitations (see `docs/limitations.md`)
5.5 Generalisability to other Polish cities / European platforms

---

## 6. Conclusions

6.1 Summary of contributions
6.2 Phase 2 outlook (socioeconomic integration, ML models)
6.3 Recommendations for platform operators (open OGC endpoints)

---

## Supplementary Materials

S1: Full source inventory CSV
S2: Complete indicator table (all spatial units)
S3: Manual annotation template
S4: Pipeline run log
S5: Python package and code repository (this repo)

---

## Target Journals

1. *International Journal of Applied Earth Observation and Geoinformation* (IF ~7.5)
2. *Computers, Environment and Urban Systems* (IF ~6.5)
3. *Energy and Buildings* (IF ~6.6)
4. *Remote Sensing* (MDPI, open access)
