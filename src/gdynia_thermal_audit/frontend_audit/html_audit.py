"""HTML landing-page audit functions."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

log = logging.getLogger("gdynia_thermal_audit.frontend_audit.html_audit")


def audit_landing_page(
    url: str,
    output_dir: Path,
    session: Any,
) -> dict[str, Any]:
    """Download and parse the landing page of the target platform.

    Parameters
    ----------
    url:
        Landing-page URL.
    output_dir:
        Directory where raw HTML and JSON inventory are saved.
    session:
        An ``httpx.Client`` (or ``requests.Session``) instance.

    Returns
    -------
    dict with keys:
        ``html_content``, ``scripts``, ``links``, ``images``,
        ``candidate_urls``, ``raw_html_path``, ``inventory_path``.
    """
    log.info("Fetching landing page: %s", url)
    response = session.get(url)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "lxml")

    scripts = [
        {"src": tag.get("src", ""), "inline": not bool(tag.get("src")), "snippet": tag.string or ""}
        for tag in soup.find_all("script")
    ]
    links = [
        {"href": tag.get("href", ""), "rel": " ".join(tag.get("rel", [])), "type": tag.get("type", "")}
        for tag in soup.find_all("link")
    ]
    images = [
        {"src": tag.get("src", ""), "alt": tag.get("alt", "")}
        for tag in soup.find_all("img")
    ]

    # Collect all candidate URLs
    candidate_urls: list[str] = []
    for s in scripts:
        if s["src"]:
            candidate_urls.append(str(s["src"]))
    for lnk in links:
        if lnk["href"] and not lnk["href"].startswith("#"):
            candidate_urls.append(str(lnk["href"]))

    # Save raw HTML
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_html_path = output_dir / "landing_page.html"
    raw_html_path.write_text(html, encoding="utf-8")
    log.info("Saved raw HTML to %s", raw_html_path)

    # Save inventory JSON
    inventory = {
        "url": url,
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "scripts": scripts,
        "links": links,
        "images": images,
        "candidate_urls": candidate_urls,
    }
    inventory_path = output_dir / "landing_page_inventory.json"
    inventory_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Saved inventory to %s", inventory_path)

    return {
        "html_content": html,
        "scripts": scripts,
        "links": links,
        "images": images,
        "candidate_urls": candidate_urls,
        "raw_html_path": str(raw_html_path),
        "inventory_path": str(inventory_path),
    }
