"""Article table export utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from gdynia_thermal_audit.reporting.summary_tables import (
    make_indicator_summary_table,
    make_source_inventory_table,
)

log = logging.getLogger("gdynia_thermal_audit.reporting.export_article_tables")


def export_all_article_tables(
    indicators_df: pd.DataFrame,
    source_inventory_df: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    """Export all article tables to CSV and LaTeX.

    Parameters
    ----------
    indicators_df:
        Per-unit indicators DataFrame.
    source_inventory_df:
        Source inventory DataFrame.
    output_dir:
        Directory where output files are written.

    Returns
    -------
    Dict mapping table name to output path.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    # Table 1: Source inventory summary
    t1 = make_source_inventory_table(source_inventory_df)
    p1_csv = output_dir / "table1_source_inventory.csv"
    p1_tex = output_dir / "table1_source_inventory.tex"
    t1.to_csv(p1_csv, index=False)
    _save_latex(t1, p1_tex, caption="Source inventory summary", label="tab:source-inventory")
    paths["table1_csv"] = p1_csv
    paths["table1_tex"] = p1_tex

    # Table 2: Full indicator data
    p2_csv = output_dir / "table2_indicators.csv"
    indicators_df.to_csv(p2_csv, index=False)
    paths["table2_csv"] = p2_csv

    # Table 3: Indicator summary statistics
    t3 = make_indicator_summary_table(indicators_df)
    p3_csv = output_dir / "table3_indicator_summary.csv"
    p3_tex = output_dir / "table3_indicator_summary.tex"
    t3.to_csv(p3_csv)
    _save_latex(t3.reset_index(), p3_tex, caption="Indicator summary statistics", label="tab:indicators")
    paths["table3_csv"] = p3_csv
    paths["table3_tex"] = p3_tex

    log.info("Exported %d article tables to %s", len(paths), output_dir)
    return paths


def _save_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    """Save a DataFrame as a LaTeX table fragment."""
    try:
        latex = df.to_latex(
            index=False,
            caption=caption,
            label=label,
            escape=True,
            float_format="%.4f",
        )
        path.write_text(latex, encoding="utf-8")
    except Exception as exc:
        log.warning("LaTeX export failed for %s: %s", path, exc)
