"""JavaScript asset inventory helpers."""

from __future__ import annotations

import re
from typing import Any

_JS_URL_RE = re.compile(r"""['"]([^'"]+\.js(?:\?[^'"]*)?)['"]\s*""")
_CONFIG_RE = re.compile(
    r"""(?:var|let|const)\s+(\w*[Cc]onfig\w*)\s*=\s*(\{[^;]+\})""",
    re.DOTALL,
)
_TILE_URL_RE = re.compile(r"""['"]([^'"]*\{[xyz]\}[^'"]*)['"]\s*""")
_WMS_RE = re.compile(r"""https?://[^\s'"]+[?&]SERVICE=WMS[^\s'"]*""", re.IGNORECASE)


def inventory_scripts(html_content: str) -> list[dict[str, Any]]:
    """Extract script references and metadata from raw HTML.

    Parameters
    ----------
    html_content:
        Raw HTML string.

    Returns
    -------
    List of dicts with keys ``type``, ``src`` / ``snippet``, ``candidate``.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "lxml")
    items: list[dict[str, Any]] = []

    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            items.append(
                {
                    "type": "external",
                    "src": src,
                    "snippet": None,
                    "candidate": _is_candidate_script(src),
                }
            )
        elif tag.string:
            snippet = tag.string.strip()[:500]
            items.append(
                {
                    "type": "inline",
                    "src": None,
                    "snippet": snippet,
                    "candidate": bool(
                        _WMS_RE.search(tag.string) or _TILE_URL_RE.search(tag.string)
                    ),
                }
            )
    return items


def extract_js_urls(js_text: str) -> list[str]:
    """Return all JS file URL strings referenced within *js_text*."""
    return _JS_URL_RE.findall(js_text)


def extract_config_refs(js_text: str) -> list[dict[str, str]]:
    """Return candidate config object variable names and their raw text."""
    return [{"name": m.group(1), "raw": m.group(2)[:200]} for m in _CONFIG_RE.finditer(js_text)]


def extract_tile_templates(js_text: str) -> list[str]:
    """Return tile URL templates (strings containing ``{x}``, ``{y}``, ``{z}``)."""
    return _TILE_URL_RE.findall(js_text)


def _is_candidate_script(src: str) -> bool:
    """Return True if the script filename suggests it contains map config."""
    name = src.lower()
    keywords = ("main", "app", "map", "viewer", "config", "bundle", "chunk")
    return any(kw in name for kw in keywords)
