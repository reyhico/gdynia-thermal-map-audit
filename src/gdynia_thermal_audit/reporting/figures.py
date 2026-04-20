"""Figure generation for reporting."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

log = logging.getLogger("gdynia_thermal_audit.reporting.figures")


def plot_indicators_map(
    zones_gdf: gpd.GeoDataFrame,
    indicators_df: pd.DataFrame,
    column: str,
    output_path: Path | str,
    title: str | None = None,
    cmap: str = "YlOrRd",
    figsize: tuple[int, int] = (10, 8),
    dpi: int = 150,
) -> Path:
    """Create a choropleth map of a single indicator.

    Parameters
    ----------
    zones_gdf:
        Spatial units GeoDataFrame.
    indicators_df:
        Indicator values DataFrame.  Must contain *column* and ``unit_id``.
    column:
        Name of the indicator column to map.
    output_path:
        File path for the saved figure.
    title:
        Map title (defaults to *column*).
    cmap:
        Matplotlib colormap name.
    figsize:
        Figure size in inches.
    dpi:
        Figure resolution.

    Returns
    -------
    Path to the saved figure.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Merge indicators onto zones
    id_col = _find_id_col(zones_gdf)
    if "unit_id" in indicators_df.columns and id_col:
        merged = zones_gdf.merge(
            indicators_df[["unit_id", column]], left_on=id_col, right_on="unit_id", how="left"
        )
    else:
        merged = zones_gdf.copy()
        if column not in merged.columns:
            merged[column] = float("nan")

    fig, ax = plt.subplots(figsize=figsize)

    if column in merged.columns and merged[column].notna().any():
        merged.plot(
            column=column,
            ax=ax,
            cmap=cmap,
            legend=True,
            legend_kwds={"label": column, "orientation": "horizontal", "shrink": 0.6},
            edgecolor="black",
            linewidth=0.5,
            missing_kwds={"color": "lightgrey", "label": "No data"},
        )
    else:
        merged.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.5)
        ax.text(
            0.5,
            0.5,
            f"No data for '{column}'",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            color="grey",
        )

    ax.set_title(title or column.replace("_", " ").title(), fontsize=14, pad=12)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved to %s", output_path)
    return output_path


def _find_id_col(gdf: gpd.GeoDataFrame) -> str | None:
    for candidate in ("district_id", "neighborhood_id", "cell_id", "id"):
        if candidate in gdf.columns:
            return candidate
    return None
