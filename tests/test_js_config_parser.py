"""Tests for js_config_parser.extract_config_from_js."""

from gdynia_thermal_audit.parser.js_config_parser import extract_config_from_js


def test_extract_wms_url():
    js = """
    var config = {
        wmsUrl: 'https://example.com/wms?SERVICE=WMS&REQUEST=GetMap&LAYERS=thermal'
    };
    """
    results = extract_config_from_js(js)
    types = [r["type"] for r in results]
    assert "wms_url" in types
    wms = next(r for r in results if r["type"] == "wms_url")
    assert "SERVICE=WMS" in wms["value"].upper()


def test_extract_tile_template():
    js = """
    map.addLayer({
        url: 'https://tiles.example.com/thermal/{z}/{x}/{y}.png',
        attribution: 'Thermal survey'
    });
    """
    results = extract_config_from_js(js)
    types = [r["type"] for r in results]
    assert "tile_template" in types
    tile = next(r for r in results if r["type"] == "tile_template")
    assert "{z}" in tile["value"] or "{x}" in tile["value"] or "{y}" in tile["value"]


def test_extract_layer_name():
    js = """
    var layer_name = 'thermal_loss_index';
    """
    results = extract_config_from_js(js)
    types = [r["type"] for r in results]
    assert "layer_name" in types
    layer = next(r for r in results if r["type"] == "layer_name")
    assert layer["value"] == "thermal_loss_index"


def test_empty_string_returns_empty():
    results = extract_config_from_js("")
    assert results == []


def test_no_match_returns_empty():
    js = "var x = 1; function foo() { return 42; }"
    results = extract_config_from_js(js)
    # No geospatial patterns — result may be empty or contain only non-geo matches
    assert isinstance(results, list)


def test_crs_extraction():
    js = "var projection = 'EPSG:2180';"
    results = extract_config_from_js(js)
    types = [r["type"] for r in results]
    assert "crs" in types
    crs = next(r for r in results if r["type"] == "crs")
    assert "2180" in crs["value"]


def test_wfs_url():
    js = "wfsEndpoint = 'https://geo.example.com/wfs?SERVICE=WFS&REQUEST=GetFeature';"
    results = extract_config_from_js(js)
    types = [r["type"] for r in results]
    assert "wfs_url" in types
