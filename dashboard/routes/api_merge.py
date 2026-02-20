"""Merge Configuration API — view/edit merge_config.json + discover columns."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from config_paths import CONFIG_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, FINAL_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.merge")
bp = Blueprint("merge_config", __name__, url_prefix="/api/merge")

CONFIG_FILE = CONFIG_DIR / "merge_config.json"

DIR_MAP = {
    "processed": PROCESSED_DATA_DIR,
    "raw": RAW_DATA_DIR,
    "final": FINAL_DATA_DIR,
}


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"output_filename": "master_dataset.csv", "datasets": {}, "merge_strategy": {"method": "concat"}}


def _save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


# ---------- Config CRUD ----------

@bp.route("/config", methods=["GET"])
def get_config():
    """Return current merge_config.json."""
    return jsonify(_load_config())


@bp.route("/config", methods=["PUT"])
def update_config():
    """Overwrite merge_config.json with the supplied JSON body."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    _save_config(data)
    logger.info("Merge config updated via dashboard")
    return jsonify({"status": "saved"})


# ---------- Column discovery ----------

@bp.route("/datasets", methods=["GET"])
def list_available_datasets():
    """Scan processed/ and raw/ for CSVs, return filename + all column headers.
    
    This lets the dashboard show a column picker even for datasets not yet
    in merge_config.json.
    """
    results = []
    seen_filenames: set[str] = set()

    for dir_label, dir_path in [("processed", PROCESSED_DATA_DIR), ("raw", RAW_DATA_DIR)]:
        if not dir_path.exists():
            continue
        for csv_file in sorted(dir_path.glob("*.csv")):
            if csv_file.name in seen_filenames:
                continue
            seen_filenames.add(csv_file.name)
            try:
                with open(csv_file, "r", encoding="utf-8") as fh:
                    reader = csv.reader(fh)
                    header = next(reader, [])
            except Exception:
                header = []
            results.append({
                "filename": csv_file.name,
                "directory": dir_label,
                "columns": header,
                "row_count": _quick_row_count(csv_file),
            })

    return jsonify(results)


def _quick_row_count(path: Path, max_scan: int = 100_000) -> int:
    """Fast approximate row count (skips header)."""
    try:
        count = 0
        with open(path, "r", encoding="utf-8") as fh:
            next(fh, None)  # skip header
            for _ in fh:
                count += 1
                if count >= max_scan:
                    break
        return count
    except Exception:
        return -1
