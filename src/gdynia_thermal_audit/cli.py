"""Typer CLI application for the Gdynia Thermal Audit pipeline."""

from __future__ import annotations

import pathlib
from typing import Annotated, Optional

import typer
from rich.console import Console

from gdynia_thermal_audit import __version__
from gdynia_thermal_audit.logging_utils import setup_logging
from gdynia_thermal_audit.settings import Settings

app = typer.Typer(
    name="gta",
    help="Gdynia Thermal Audit — Phase 1 pipeline CLI.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

# ---------------------------------------------------------------------------
# Version callback
# ---------------------------------------------------------------------------


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"gta version {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    """Gdynia Thermal Map Audit pipeline."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_settings() -> Settings:
    return Settings()


def _setup(settings: Settings) -> None:
    setup_logging(level=settings.log_level)


# ---------------------------------------------------------------------------
# Frontend audit commands
# ---------------------------------------------------------------------------


@app.command("audit-site")
def audit_site(
    url: Annotated[Optional[str], typer.Option("--url", "-u")] = None,
    output_dir: Annotated[Optional[pathlib.Path], typer.Option("--output-dir")] = None,
) -> None:
    """Download and snapshot the target platform landing page."""
    import httpx

    from gdynia_thermal_audit.frontend_audit.html_audit import audit_landing_page
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    effective_url = url or settings.target_url
    effective_out = output_dir or (pathlib.Path(settings.data_dir) / "raw")
    ensure_dir(effective_out)

    console.print(f"[bold]Auditing:[/bold] {effective_url}")
    with httpx.Client(
        timeout=30, follow_redirects=True, headers={"User-Agent": settings.user_agent}
    ) as session:
        results = audit_landing_page(effective_url, effective_out, session)
    console.print(f"[green]Done.[/green] Found {len(results.get('scripts', []))} script(s).")


@app.command("inspect-viewer")
def inspect_viewer(
    url: Annotated[Optional[str], typer.Option("--url", "-u")] = None,
) -> None:
    """Snapshot the viewer page HTML and record metadata."""
    import httpx

    from gdynia_thermal_audit.frontend_audit.viewer_snapshot import snapshot_viewer
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    effective_url = url or settings.viewer_url
    out_dir = pathlib.Path(settings.data_dir) / "raw"
    ensure_dir(out_dir)

    console.print(f"[bold]Snapshotting viewer:[/bold] {effective_url}")
    with httpx.Client(
        timeout=30, follow_redirects=True, headers={"User-Agent": settings.user_agent}
    ) as session:
        meta = snapshot_viewer(effective_url, out_dir, session)
    console.print(f"[green]Done.[/green] Metadata: {meta}")


@app.command("inventory-assets")
def inventory_assets(
    create_annotation_template: Annotated[bool, typer.Option()] = False,
) -> None:
    """Run asset inventory from the raw HTML snapshots."""
    from gdynia_thermal_audit.frontend_audit.asset_catalog import build_asset_catalog
    from gdynia_thermal_audit.utils.io import ensure_dir, save_csv

    settings = _get_settings()
    _setup(settings)
    interim = pathlib.Path(settings.data_dir) / "interim"
    ensure_dir(interim)

    # Load raw HTML if available
    raw_html_path = pathlib.Path(settings.data_dir) / "raw" / "landing_page.html"
    if raw_html_path.exists():
        html_content = raw_html_path.read_text(encoding="utf-8", errors="replace")
        from gdynia_thermal_audit.frontend_audit.js_inventory import inventory_scripts

        js_items = inventory_scripts(html_content)
        audit_results = {"html_content": html_content, "scripts": js_items}
    else:
        console.print("[yellow]Warning:[/yellow] No landing_page.html found; using empty inventory.")
        audit_results = {}

    df = build_asset_catalog(audit_results)
    save_csv(df, interim / "asset_catalog.csv")
    console.print(f"[green]Asset catalog saved.[/green] {len(df)} records.")

    if create_annotation_template:
        from gdynia_thermal_audit.annotation.templates import create_annotation_csv

        ann_path = pathlib.Path(settings.data_dir) / "annotations" / "annotations.csv"
        ensure_dir(ann_path.parent)
        create_annotation_csv(ann_path)
        console.print(f"[green]Annotation template saved:[/green] {ann_path}")


@app.command("probe-endpoints")
def probe_endpoints(
    candidates_file: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Probe discovered endpoints and check OGC capabilities."""
    import pandas as pd
    import httpx

    from gdynia_thermal_audit.network_probe.service_discovery import discover_services
    from gdynia_thermal_audit.utils.io import ensure_dir, save_csv

    settings = _get_settings()
    _setup(settings)
    interim = pathlib.Path(settings.data_dir) / "interim"
    ensure_dir(interim)

    if candidates_file and candidates_file.exists():
        df = pd.read_csv(candidates_file)
        urls = df["url"].dropna().tolist()
    else:
        # Use demo data as fallback
        demo_path = pathlib.Path(settings.data_dir) / "demo" / "demo_source_inventory.csv"
        if demo_path.exists():
            df = pd.read_csv(demo_path)
            urls = df["url"].dropna().tolist()
            console.print("[yellow]Using demo source inventory.[/yellow]")
        else:
            urls = [settings.target_url]

    console.print(f"Probing {len(urls)} URLs …")
    results = discover_services(urls)
    df_out = pd.DataFrame([r.__dict__ if hasattr(r, "__dict__") else dict(r) for r in results])
    save_csv(df_out, interim / "probe_results.csv")
    console.print(f"[green]Probe complete.[/green] Results: {interim / 'probe_results.csv'}")


@app.command("fetch-assets")
def fetch_assets(
    inventory_file: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Download recoverable assets listed in the source inventory."""
    import pandas as pd

    from gdynia_thermal_audit.downloader.fetch import fetch_resource
    from gdynia_thermal_audit.utils.io import ensure_dir
    import httpx

    settings = _get_settings()
    _setup(settings)
    raw = pathlib.Path(settings.data_dir) / "raw"
    ensure_dir(raw)

    inv_path = inventory_file or (pathlib.Path(settings.data_dir) / "interim" / "asset_catalog.csv")
    if not inv_path.exists():
        console.print("[yellow]No inventory file found; nothing to fetch.[/yellow]")
        raise typer.Exit()

    df = pd.read_csv(inv_path)
    downloaded = 0
    with httpx.Client(
        timeout=30, follow_redirects=True, headers={"User-Agent": settings.user_agent}
    ) as session:
        for _, row in df.iterrows():
            url = row.get("url")
            if not url or str(url).startswith("data:"):
                continue
            local = raw / pathlib.Path(url).name
            ok = fetch_resource(url, local, session, settings.request_delay_s, settings.max_retries)
            if ok:
                downloaded += 1
    console.print(f"[green]Fetched {downloaded} assets.[/green]")


@app.command("parse-configs")
def parse_configs(
    js_dir: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Parse JavaScript config files for layer definitions and endpoint URLs."""
    import json

    from gdynia_thermal_audit.parser.js_config_parser import extract_config_from_js
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    effective_js_dir = js_dir or (pathlib.Path(settings.data_dir) / "raw" / "js")
    out_dir = pathlib.Path(settings.data_dir) / "interim" / "js_configs"
    ensure_dir(out_dir)

    if not effective_js_dir.exists():
        console.print("[yellow]No JS directory found.[/yellow]")
        raise typer.Exit()

    for js_file in effective_js_dir.glob("*.js"):
        text = js_file.read_text(encoding="utf-8", errors="replace")
        configs = extract_config_from_js(text)
        out_path = out_dir / (js_file.stem + "_configs.json")
        out_path.write_text(json.dumps(configs, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"  Extracted {len(configs)} config(s) from {js_file.name}")


@app.command("build-layer-catalog")
def build_layer_catalog(
    probe_file: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Build the layer catalog from discovered services."""
    import pandas as pd

    from gdynia_thermal_audit.parser.layer_catalog_builder import build_layer_catalog as _build
    from gdynia_thermal_audit.utils.io import ensure_dir, save_csv

    settings = _get_settings()
    _setup(settings)
    interim = pathlib.Path(settings.data_dir) / "interim"
    ensure_dir(interim)

    src = probe_file or (interim / "probe_results.csv")
    if src.exists():
        df = pd.read_csv(src)
        sources = df.to_dict(orient="records")
    else:
        console.print("[yellow]No probe results; building empty catalog.[/yellow]")
        sources = []

    df_cat = _build(sources)
    save_csv(df_cat, interim / "layer_catalog.csv")
    console.print(f"[green]Layer catalog:[/green] {len(df_cat)} layers.")


@app.command("import-districts")
def import_districts(
    source: Annotated[pathlib.Path, typer.Argument()] = pathlib.Path(
        "data/demo/demo_districts.geojson"
    ),
) -> None:
    """Import district boundaries into the processed GeoPackage."""
    from gdynia_thermal_audit.spatial_units.districts import load_districts, validate_districts
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"
    ensure_dir(processed)

    gdf = load_districts(source)
    validate_districts(gdf)
    gdf.to_file(processed / "spatial_units.gpkg", layer="districts", driver="GPKG")
    console.print(f"[green]Imported {len(gdf)} districts.[/green]")


@app.command("import-neighborhoods")
def import_neighborhoods(
    source: Annotated[pathlib.Path, typer.Argument()],
) -> None:
    """Import neighborhood boundaries into the processed GeoPackage."""
    from gdynia_thermal_audit.spatial_units.neighborhoods import (
        load_neighborhoods,
        validate_neighborhoods,
    )
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"
    ensure_dir(processed)

    gdf = load_neighborhoods(source)
    validate_neighborhoods(gdf)
    gdf.to_file(processed / "spatial_units.gpkg", layer="neighborhoods", driver="GPKG")
    console.print(f"[green]Imported {len(gdf)} neighborhoods.[/green]")


@app.command("build-grid")
def build_grid(
    size: Annotated[int, typer.Option("--size", "-s", help="Cell size in metres (100/250/500)")] = 250,
) -> None:
    """Generate a regular square-cell grid covering Gdynia."""
    from pyproj import Transformer

    from gdynia_thermal_audit.constants import EPSG_POLAND, GDYNIA_BBOX_WGS84
    from gdynia_thermal_audit.spatial_units.grid import export_grid, generate_grid
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"
    ensure_dir(processed)

    if size not in (100, 250, 500):
        console.print(f"[red]Invalid size {size}. Use 100, 250, or 500.[/red]")
        raise typer.Exit(1)

    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{EPSG_POLAND}", always_xy=True)
    xmin, ymin = transformer.transform(GDYNIA_BBOX_WGS84[0], GDYNIA_BBOX_WGS84[1])
    xmax, ymax = transformer.transform(GDYNIA_BBOX_WGS84[2], GDYNIA_BBOX_WGS84[3])

    gdf = generate_grid((xmin, ymin, xmax, ymax), cell_size_m=size, epsg=EPSG_POLAND)
    export_grid(gdf, processed, cell_size_m=size)
    console.print(f"[green]Grid ({size} m):[/green] {len(gdf)} cells → {processed}")


@app.command("compute-raster-indicators")
def compute_raster_indicators(
    raster: Annotated[pathlib.Path, typer.Argument()],
    units_layer: Annotated[str, typer.Option()] = "districts",
) -> None:
    """Compute raster-based thermal indicators (Scenario A)."""
    import geopandas as gpd

    from gdynia_thermal_audit.indicators.raster_indicators import compute_raster_indicators as _compute
    from gdynia_thermal_audit.utils.io import ensure_dir, save_csv

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"
    ensure_dir(processed)

    gdf = gpd.read_file(processed / "spatial_units.gpkg", layer=units_layer)
    df = _compute(gdf, raster)
    save_csv(df, processed / f"indicators_{units_layer}_raster.csv")
    console.print(f"[green]Raster indicators computed.[/green] {len(df)} units.")


@app.command("compute-vector-indicators")
def compute_vector_indicators(
    features: Annotated[pathlib.Path, typer.Argument()],
    units_layer: Annotated[str, typer.Option()] = "districts",
) -> None:
    """Compute vector-based thermal indicators (Scenario B)."""
    import geopandas as gpd

    from gdynia_thermal_audit.indicators.vector_indicators import compute_vector_indicators as _compute
    from gdynia_thermal_audit.utils.io import ensure_dir, save_csv

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"

    gdf_zones = gpd.read_file(processed / "spatial_units.gpkg", layer=units_layer)
    gdf_feat = gpd.read_file(features)
    df = _compute(gdf_zones, gdf_feat)
    save_csv(df, processed / f"indicators_{units_layer}_vector.csv")
    console.print(f"[green]Vector indicators computed.[/green] {len(df)} units.")


@app.command("compute-annotation-indicators")
def compute_annotation_indicators(
    annotations: Annotated[Optional[pathlib.Path], typer.Option()] = None,
    units_layer: Annotated[str, typer.Option()] = "districts",
) -> None:
    """Compute annotation-based thermal indicators (Scenario C)."""
    import geopandas as gpd
    import pandas as pd

    from gdynia_thermal_audit.indicators.annotation_indicators import (
        compute_annotation_indicators as _compute,
    )
    from gdynia_thermal_audit.utils.io import ensure_dir, save_csv

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"
    ensure_dir(processed)

    ann_path = annotations or (pathlib.Path(settings.data_dir) / "annotations" / "annotations.csv")
    if not ann_path.exists():
        ann_path = pathlib.Path(settings.data_dir) / "demo" / "demo_annotations.csv"
        console.print("[yellow]Using demo annotations.[/yellow]")

    df_ann = pd.read_csv(ann_path)

    gpkg = processed / "spatial_units.gpkg"
    if gpkg.exists():
        gdf_zones = gpd.read_file(gpkg, layer=units_layer)
    else:
        from gdynia_thermal_audit.spatial_units.districts import get_gdynia_districts_placeholder
        gdf_zones = get_gdynia_districts_placeholder()

    df = _compute(gdf_zones, df_ann)
    save_csv(df, processed / f"indicators_{units_layer}_annotation.csv")
    console.print(f"[green]Annotation indicators computed.[/green] {len(df)} units.")


@app.command("compute-indicators")
def compute_indicators(
    scenario: Annotated[
        str,
        typer.Option("--scenario", "-s", help="auto | raster | vector | annotation"),
    ] = "auto",
    units_layer: Annotated[str, typer.Option()] = "districts",
) -> None:
    """Run all available indicator computations."""
    console.print(f"Running indicators with scenario=[bold]{scenario}[/bold] …")
    if scenario in ("auto", "annotation"):
        ctx = typer.Context(compute_annotation_indicators)
        compute_annotation_indicators(units_layer=units_layer)
    console.print("[green]Indicator computation complete.[/green]")


@app.command("validate-annotations")
def validate_annotations_cmd(
    annotations: Annotated[Optional[pathlib.Path], typer.Argument()] = None,
) -> None:
    """Validate an annotation CSV file."""
    import pandas as pd

    from gdynia_thermal_audit.annotation.validate import validate_annotations

    settings = _get_settings()
    _setup(settings)
    path = annotations or (pathlib.Path(settings.data_dir) / "annotations" / "annotations.csv")
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)

    df = pd.read_csv(path)
    is_valid, errors = validate_annotations(df)
    if is_valid:
        console.print(f"[green]✓ All {len(df)} records passed validation.[/green]")
    else:
        console.print(f"[red]✗ {len(errors)} validation error(s):[/red]")
        for e in errors:
            console.print(f"  [red]·[/red] {e}")
        raise typer.Exit(1)


@app.command("merge-annotations")
def merge_annotations_cmd(
    existing: Annotated[pathlib.Path, typer.Argument()],
    new: Annotated[pathlib.Path, typer.Argument()],
    output: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Merge a new annotation CSV into an existing one, deduplicating by record_id."""
    import pandas as pd

    from gdynia_thermal_audit.annotation.merge import merge_annotations
    from gdynia_thermal_audit.utils.io import save_csv

    settings = _get_settings()
    _setup(settings)
    df_existing = pd.read_csv(existing)
    df_new = pd.read_csv(new)
    merged = merge_annotations(df_existing, df_new)
    out = output or existing
    save_csv(merged, out)
    console.print(f"[green]Merged:[/green] {len(merged)} records → {out}")


@app.command("export-article-tables")
def export_article_tables(
    indicators_file: Annotated[Optional[pathlib.Path], typer.Option()] = None,
    source_inventory_file: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Export publication-ready tables."""
    import pandas as pd

    from gdynia_thermal_audit.reporting.export_article_tables import export_all_article_tables
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    processed = pathlib.Path(settings.data_dir) / "processed"
    out = pathlib.Path(settings.output_dir) / "tables"
    ensure_dir(out)

    ind_path = indicators_file or next(processed.glob("indicators_districts_*.csv"), None)
    if ind_path is None or not ind_path.exists():
        ind_path = pathlib.Path(settings.data_dir) / "demo" / "demo_annotations.csv"
        console.print("[yellow]Using demo data for indicators.[/yellow]")

    inv_path = source_inventory_file or (pathlib.Path(settings.data_dir) / "demo" / "demo_source_inventory.csv")
    df_ind = pd.read_csv(ind_path)
    df_inv = pd.read_csv(inv_path)
    export_all_article_tables(df_ind, df_inv, out)
    console.print(f"[green]Tables exported to {out}[/green]")


@app.command("export-figures")
def export_figures(
    indicators_file: Annotated[Optional[pathlib.Path], typer.Option()] = None,
) -> None:
    """Export publication-ready figures."""
    import pandas as pd

    from gdynia_thermal_audit.reporting.figures import plot_indicators_map
    from gdynia_thermal_audit.spatial_units.districts import get_gdynia_districts_placeholder
    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    fig_dir = pathlib.Path(settings.output_dir) / "figures"
    ensure_dir(fig_dir)

    gdf = get_gdynia_districts_placeholder()
    ind_path = indicators_file or (
        pathlib.Path(settings.data_dir) / "demo" / "demo_annotations.csv"
    )
    df = pd.read_csv(ind_path)
    if "priority_index" in df.columns:
        plot_indicators_map(gdf, df, "priority_index", fig_dir / "priority_index.png")
    console.print(f"[green]Figures exported to {fig_dir}[/green]")


@app.command("run-pipeline")
def run_pipeline(
    scenario: Annotated[str, typer.Option("--scenario", "-s")] = "auto",
    demo: Annotated[bool, typer.Option("--demo/--no-demo")] = False,
    config: Annotated[Optional[pathlib.Path], typer.Option("--config")] = None,
) -> None:
    """Run the full Phase 1 pipeline end-to-end."""
    import uuid
    import datetime

    from gdynia_thermal_audit.utils.io import ensure_dir

    settings = _get_settings()
    _setup(settings)
    run_id = str(uuid.uuid4())
    start = datetime.datetime.utcnow().isoformat() + "Z"
    console.rule(f"[bold]GTA Pipeline[/bold]  run_id={run_id}")
    console.print(f"  scenario : {scenario}")
    console.print(f"  demo     : {demo}")
    console.print(f"  start    : {start}")

    ensure_dir(pathlib.Path(settings.output_dir) / "logs")

    steps = []
    if not demo:
        console.print("\n[bold]Step 1:[/bold] Audit site …")
        audit_site()
        steps.append("audit_site")

        console.print("\n[bold]Step 2:[/bold] Inventory assets …")
        inventory_assets()
        steps.append("inventory_assets")

        console.print("\n[bold]Step 3:[/bold] Probe endpoints …")
        probe_endpoints()
        steps.append("probe_endpoints")

        console.print("\n[bold]Step 4:[/bold] Build layer catalog …")
        build_layer_catalog()
        steps.append("build_layer_catalog")

    console.print("\n[bold]Step 5:[/bold] Build grid …")
    build_grid(size=250)
    steps.append("build_grid")

    console.print("\n[bold]Step 6:[/bold] Compute indicators …")
    compute_indicators(scenario=scenario)
    steps.append("compute_indicators")

    console.print("\n[bold]Step 7:[/bold] Export tables …")
    export_article_tables()
    steps.append("export_article_tables")

    end = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    console.rule(f"[green]Pipeline complete[/green]  steps={len(steps)}")
    console.print(f"  end: {end}")
