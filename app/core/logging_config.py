"""Logging configuration for the application."""

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure application logging once without exposing configuration secrets."""
    logging.basicConfig(
        level=logging.DEBUG if get_settings().debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
