"""Clean API — manage cleaning configuration."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from config_paths import CONFIG_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.clean")
bp = Blueprint("clean", __name__, url_prefix="/api/clean")

CONFIG_FILE = CONFIG_DIR / "clean_config.json"

DEFAULT_CONFIG = {
    "drop_empty_rows": True,
    "empty_row_threshold": 0.5,
    "detect_outliers": True,
    "outlier_iqr_factor": 1.5,
    "fix_dtypes": True,
    "standardize_columns": True,
    "remove_duplicates": True,
}


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def _save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


@bp.route("/config", methods=["GET"])
def get_config():
    return jsonify(_load_config())


@bp.route("/config", methods=["PUT"])
def update_config():
    data = request.get_json()
    _save_config(data)
    logger.info("Updated clean config")
    return jsonify({"status": "ok"})
