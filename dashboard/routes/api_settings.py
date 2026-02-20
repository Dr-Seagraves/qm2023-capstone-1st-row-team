"""Settings API — manage data sources and column configuration."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from dashboard.services.config_manager import (
    get_sources, save_sources, get_column_config, save_column_config,
)
from logging_config import setup_logger

logger = setup_logger("dashboard.settings")
bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@bp.route("/sources", methods=["GET"])
def list_sources():
    sources = get_sources()
    return jsonify(sources)


@bp.route("/sources", methods=["PUT"])
def update_sources():
    data = request.get_json()
    urls = data.get("urls", [])
    save_sources(urls)
    logger.info("Updated data sources: %d URLs", len(urls))
    return jsonify({"status": "ok", "count": len(urls)})


@bp.route("/columns", methods=["GET"])
def list_columns():
    config = get_column_config()
    return jsonify(config)


@bp.route("/columns", methods=["PUT"])
def update_columns():
    data = request.get_json()
    save_column_config(data)
    logger.info("Updated column config")
    return jsonify({"status": "ok"})
