# Data Sources

This document catalogues all potential data sources for the Gdynia Thermal Map Audit project.

---

## 1. Primary Target: termalne.obliview.com

The primary subject of the audit is the public web map platform operated at
<https://termalne.obliview.com>.  Access is public; no credentials are required.

**Known characteristics (pre-audit)**
- Web map viewer (likely Leaflet or OpenLayers)
- Displays thermal-loss imagery of Gdynia buildings
- Origin of the thermal data: aerial infrared survey commissioned by the City of Gdynia

**Discovery strategy**
1. Download and parse the landing page HTML.
2. Extract all JavaScript file URLs and inline scripts.
3. Parse JS for WMS/WMTS/WFS endpoint strings, layer IDs, tile URL templates.
4. Probe discovered endpoints with OGC `GetCapabilities` requests.

---

## 2. OGC Web Services

### 2.1 WMS (Web Map Service)

Standard HTTP protocol for retrieving map images.  Expected endpoints tested during probing:

```
/wms
/geoserver/wms
/mapserver/wms
?SERVICE=WMS&REQUEST=GetCapabilities
```

`owslib.wms.WebMapService` is used to parse capabilities and enumerate layers.

### 2.2 WMTS (Web Map Tile Service)

RESTful tiled raster service.  Tile URL templates of the form
`{serviceUrl}/{layer}/{TileMatrixSet}/{z}/{y}/{x}.png` are extracted from JS configs.
`owslib.wmts.WebMapTileService` is used when a capabilities document is found.

`mercantile` is used to enumerate tile coordinates within Gdynia's bounding box for
a given zoom level.

### 2.3 WFS (Web Feature Service)

Returns vector features (GML/GeoJSON).  Probing tests for:

```
?SERVICE=WFS&REQUEST=GetCapabilities
?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=…&OUTPUTFORMAT=application/json
```

### 2.4 ArcGIS REST Services

If the platform uses Esri technology, endpoints may follow the pattern:

```
/arcgis/rest/services/{folder}/{service}/MapServer
/arcgis/rest/services/{folder}/{service}/FeatureServer
```

These are probed and, if discovered, the REST API is queried for layer metadata.

---

## 3. Administrative Boundaries

### 3.1 PRG (Państwowy Rejestr Granic)

The Polish National Register of Boundaries provides authoritative administrative unit
polygons at all levels (gmina, powiat, województwo, obręb).

- **Download URL**: <https://www.geoportal.gov.pl/pl/dane/panstwowy-rejestr-granic/>
- **Format**: SHP / GPKG / GML
- **CRS**: EPSG:2180 (PL-1992)
- **Licence**: Public domain

### 3.2 Gdynia Open Data Portal

The City of Gdynia may publish district and neighborhood boundaries:

- <https://otwartedane.gdynia.pl>
- Format: GeoJSON / SHP
- Update frequency: irregular

### 3.3 Fallback: Approximate Boundaries

When official boundaries cannot be retrieved, the `spatial_units.districts` module
provides a `get_gdynia_districts_placeholder()` function returning simplified synthetic
polygons for development and testing.

---

## 4. Building Footprints

### 4.1 OpenStreetMap

OSM building footprints can be fetched via the Overpass API or downloaded from
Geofabrik (Poland extract).  Fields: `building`, `building:levels`, `addr:street`.

- **Overpass API**: <https://overpass-api.de>
- **Geofabrik PL**: <https://download.geofabrik.de/europe/poland.html>
- **Licence**: ODbL

### 4.2 BDOT10k (Baza Danych Obiektów Topograficznych)

Polish 1:10 000 topographic database includes building outlines with attributes.

- **Source**: GUGiK <https://www.geoportal.gov.pl>
- **Format**: GML / SHP
- **Licence**: Public domain

---

## 5. Satellite / Aerial Imagery (Reference)

| Source | Type | Notes |
|---|---|---|
| Google Maps Static API | RGB aerial | Requires API key; terms restrict bulk download |
| Bing Maps | RGB aerial | Requires API key |
| Geoportal krajowy | RGB orthophoto | 25 cm resolution; public WMS |
| Sentinel-2 (Copernicus) | Multispectral | Free; 10 m resolution; thermal via Landsat 8/9 TIR |

Imagery sources are listed here for reference.  Phase 1 does not perform bulk raster
download; rasters are only downloaded if directly served by the target platform.

---

## 6. Synthetic / Demo Data

The `data/demo/` directory contains synthetic datasets for development and CI testing:

| File | Description |
|---|---|
| `demo_districts.geojson` | 4 simplified Gdynia district polygons |
| `demo_annotations.csv` | 10 synthetic manual annotation records |
| `demo_source_inventory.csv` | 5 synthetic source inventory records |
| `demo_layer_catalog.csv` | 5 synthetic layer catalog records |
| `demo_fetch_log.csv` | 5 synthetic fetch log records |

These data are entirely fictional and must not be used in published analysis.
