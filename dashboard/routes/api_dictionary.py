"""Data Dictionary API."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from config_paths import FINAL_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.dictionary")
bp = Blueprint("dictionary", __name__, url_prefix="/api/dictionary")

DICT_JSON = FINAL_DATA_DIR / "data_dictionary.json"


@bp.route("", methods=["GET"])
def get_dictionary():
    if DICT_JSON.exists():
        data = json.loads(DICT_JSON.read_text(encoding="utf-8"))
        return jsonify(data)
    return jsonify({"version": "1.0", "datasets": {}})


@bp.route("", methods=["PUT"])
def update_dictionary():
    data = request.get_json()
    DICT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(DICT_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    logger.info("Updated data dictionary")
    return jsonify({"status": "ok"})


@bp.route("/scan", methods=["POST"])
def scan_dictionary():
    """Re-scan CSVs and regenerate dictionary, then auto-populate column config."""
    try:
        from generate_data_dictionary import main as gen_main
        dictionary = gen_main()

        # Auto-populate config/column_config.json from the scanned dictionary
        _sync_column_config(dictionary)

        return jsonify({"status": "ok", "datasets": len(dictionary.get("datasets", {}))})
    except Exception as exc:
        logger.error("Failed to scan: %s", exc, exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 500


def _sync_column_config(dictionary: dict):
    """Write column_config.json from the data dictionary's datasets."""
    from dashboard.services.config_manager import save_column_config
    datasets = dictionary.get("datasets", {})
    col_cfg: dict = {}
    for ds_key, ds_info in datasets.items():
        cols = {}
        for col_name, col_meta in ds_info.get("columns", {}).items():
            cols[col_name] = {
                "dtype": col_meta.get("dtype", "unknown"),
                "include": col_meta.get("include", True),
            }
        col_cfg[ds_key] = {"columns": cols}
    save_column_config(col_cfg)
    logger.info("Auto-populated column_config.json with %d datasets", len(col_cfg))
