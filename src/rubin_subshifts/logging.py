"""Logging configuration for command-line and application entry points."""

from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure a concise package-wide logging format."""
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")
