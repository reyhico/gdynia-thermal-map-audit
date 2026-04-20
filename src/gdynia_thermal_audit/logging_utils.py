"""Rich-based logging configuration."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rich_markup: bool = True,
) -> None:
    """Configure the root logger and the package logger.

    Parameters
    ----------
    level:
        Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    log_file:
        Optional path for a rotating file handler.  If *None*, only the
        console handler is attached.
    rich_markup:
        If *True* and ``rich`` is installed, use :class:`rich.logging.RichHandler`
        for coloured console output.  Falls back to a plain ``StreamHandler``
        if ``rich`` is not available.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Build console handler
    console_handler: logging.Handler
    if rich_markup:
        try:
            from rich.logging import RichHandler  # type: ignore[import-untyped]

            console_handler = RichHandler(
                level=numeric_level,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
            )
            console_handler.setLevel(numeric_level)
        except ImportError:
            console_handler = _plain_stream_handler(numeric_level)
    else:
        console_handler = _plain_stream_handler(numeric_level)

    handlers: list[logging.Handler] = [console_handler]

    # Optional file handler
    if log_file is not None:
        from logging.handlers import RotatingFileHandler

        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        file_handler.setFormatter(fmt)
        handlers.append(file_handler)

    # Configure package logger
    pkg_logger = logging.getLogger("gdynia_thermal_audit")
    pkg_logger.setLevel(logging.DEBUG)
    pkg_logger.handlers.clear()
    for h in handlers:
        pkg_logger.addHandler(h)
    pkg_logger.propagate = False

    # Quieten noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3", "rasterio", "fiona"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the package namespace.

    Parameters
    ----------
    name:
        Dot-separated module name (relative to the package root is fine).
    """
    return logging.getLogger(f"gdynia_thermal_audit.{name}")


def _plain_stream_handler(level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler.setFormatter(fmt)
    return handler
