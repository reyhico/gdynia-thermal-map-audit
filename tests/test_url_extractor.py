"""Tests for url_extractor module."""

import pytest

from gdynia_thermal_audit.parser.url_extractor import (
    classify_url,
    extract_geospatial_urls,
    extract_urls,
)


def test_extract_urls_basic():
    text = "See https://example.com and http://other.org for details."
    urls = extract_urls(text)
    assert any(u == "https://example.com" for u in urls)
    assert any(u == "http://other.org" for u in urls)


def test_extract_urls_deduplication():
    text = "https://example.com https://example.com https://other.com"
    urls = extract_urls(text)
    assert urls.count("https://example.com") == 1


def test_extract_urls_empty():
    assert extract_urls("") == []
    assert extract_urls("no urls here at all") == []


def test_classify_url_wms():
    url = "https://geo.example.com/ows?SERVICE=WMS&REQUEST=GetMap"
    assert classify_url(url) == "wms"


def test_classify_url_wmts():
    url = "https://geo.example.com/wmts?SERVICE=WMTS&REQUEST=GetCapabilities"
    assert classify_url(url) == "wmts"


def test_classify_url_wfs():
    url = "https://geo.example.com/wfs?SERVICE=WFS&REQUEST=GetFeature"
    assert classify_url(url) == "wfs"


def test_classify_url_geojson():
    url = "https://data.example.com/districts.geojson"
    assert classify_url(url) == "geojson"


def test_classify_url_geotiff():
    for ext in (".tif", ".tiff", ".geotiff"):
        url = f"https://data.example.com/thermal{ext}"
        assert classify_url(url) == "geotiff", f"Failed for {url}"


def test_classify_url_tile():
    url = "https://tiles.example.com/thermal/{z}/{x}/{y}.png"
    assert classify_url(url) == "tile"


def test_classify_url_unknown():
    url = "https://example.com/about"
    assert classify_url(url) == "unknown"


def test_classify_url_case_insensitive():
    url = "https://geo.example.com/wms?service=WMS&request=GetMap"
    assert classify_url(url) == "wms"


def test_extract_geospatial_urls():
    text = (
        "Check https://plain.example.com and "
        "https://geo.example.com/wfs?SERVICE=WFS&REQUEST=GetCapabilities "
        "and https://tiles.example.com/{z}/{x}/{y}.png"
    )
    geo = extract_geospatial_urls(text)
    assert isinstance(geo, list)
    assert all("url" in item and "type" in item for item in geo)
    types = [item["type"] for item in geo]
    assert "wfs" in types
    assert "tile" in types
    # Plain URL should not appear
    urls = [item["url"] for item in geo]
    assert not any(u.startswith("https://plain.example.com") for u in urls)
