"""JavaScript configuration parser."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

log = logging.getLogger("gdynia_thermal_audit.parser.js_config_parser")

# Patterns targeting common map-config patterns in bundled JS
_WMS_URL_RE = re.compile(
    r"""['"]?(https?://[^\s'"]+(?:\?|&)SERVICE=WMS[^\s'"]*?)['"]?""",
    re.IGNORECASE,
)
_TILE_URL_RE = re.compile(
    r"""['"]?(https?://[^\s'"]*\{[xyz]\}[^\s'"]*?)['"]?""",
    re.IGNORECASE,
)
_WFS_URL_RE = re.compile(
    r"""['"]?(https?://[^\s'"]+(?:\?|&)SERVICE=WFS[^\s'"]*?)['"]?""",
    re.IGNORECASE,
)
_JSON_OBJ_RE = re.compile(
    r"""(?:var|let|const)\s+\w+\s*=\s*(\{[^;]{20,}\});""",
    re.DOTALL,
)
_LAYER_DEF_RE = re.compile(
    r"""(?:layers?|layer_name|layerName)\s*[=:]\s*['"]([^'"]+)['"]""",
    re.IGNORECASE,
)
_CRS_RE = re.compile(
    r"""(?:crs|projection|srs)\s*[=:]\s*['"]?(EPSG:\d+|EPSG%3A\d+)['"]?""",
    re.IGNORECASE,
)


def extract_config_from_js(js_text: str) -> list[dict[str, Any]]:
    """Extract configuration fragments from a JavaScript bundle.

    Searches for WMS/WFS URLs, tile URL templates, JSON config objects,
    layer name declarations, and CRS strings.

    Parameters
    ----------
    js_text:
        JavaScript source code as a string.

    Returns
    -------
    List of dicts, each representing an extracted config fragment with
    keys ``type`` and ``value`` (plus any parsed subfields).
    """
    if not js_text:
        return []

    results: list[dict[str, Any]] = []

    for m in _WMS_URL_RE.finditer(js_text):
        results.append({"type": "wms_url", "value": m.group(1)})

    for m in _WFS_URL_RE.finditer(js_text):
        results.append({"type": "wfs_url", "value": m.group(1)})

    for m in _TILE_URL_RE.finditer(js_text):
        results.append({"type": "tile_template", "value": m.group(1)})

    for m in _LAYER_DEF_RE.finditer(js_text):
        results.append({"type": "layer_name", "value": m.group(1)})

    for m in _CRS_RE.finditer(js_text):
        crs_val = m.group(1).replace("%3A", ":").upper()
        results.append({"type": "crs", "value": crs_val})

    for m in _JSON_OBJ_RE.finditer(js_text):
        raw = m.group(1)
        # Attempt JSON parse (may fail for JS objects with unquoted keys)
        try:
            parsed = json.loads(raw)
            results.append({"type": "json_config", "value": parsed, "raw": raw[:200]})
        except json.JSONDecodeError:
            results.append({"type": "json_config_unparsed", "raw": raw[:200]})

    log.debug("Extracted %d config fragments from JS (%d chars)", len(results), len(js_text))
    return results
