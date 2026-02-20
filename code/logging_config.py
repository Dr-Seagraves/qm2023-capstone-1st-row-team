"""
Centralized Logging Configuration
===================================

Provides rotating file handlers for each module area plus a console handler.
Every script should call setup_logger(__name__) to get its logger.

Usage:
    from logging_config import setup_logger
    logger = setup_logger(__name__)
    logger.info("Starting download...")
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Resolve logs directory relative to this file (code/ -> project root -> logs/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LOGS_DIR = _PROJECT_ROOT / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Log format
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Rotation settings: 5 MB per file, 3 backups
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

# Module -> log file mapping
MODULE_LOG_MAP = {
    "fetch": "fetch.log",
    "clean": "clean.log",
    "filter": "filter.log",
    "merge": "merge.log",
    "dashboard": "dashboard.log",
    "pipeline": "pipeline.log",
    "general": "general.log",
}


def _get_log_category(name: str) -> str:
    """Map a logger name to a log file category."""
    name_lower = name.lower()
    for category in MODULE_LOG_MAP:
        if category in name_lower:
            return category
    return "general"


def setup_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Create and configure a logger with file + console handlers.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default DEBUG)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # File handler (rotating, per-category)
    category = _get_log_category(name)
    log_file = _LOGS_DIR / MODULE_LOG_MAP[category]
    file_handler = RotatingFileHandler(
        log_file, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
