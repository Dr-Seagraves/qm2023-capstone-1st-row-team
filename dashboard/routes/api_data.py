"""
Data Management API
====================

Column configuration, master dataset rebuild, and data viewer.
Merges column_config.json (include/exclude state) with
data_dictionary.json (metadata like dtype, row counts).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from config_paths import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, FINAL_DATA_DIR, CONFIG_DIR,
)
from logging_config import setup_logger

logger = setup_logger("dashboard.data")
bp = Blueprint("data", __name__, url_prefix="/api/data")

COLUMN_CONFIG = CONFIG_DIR / "column_config.json"
DATA_DICT = FINAL_DATA_DIR / "data_dictionary.json"
MASTER_CSV = FINAL_DATA_DIR / "master_dataset.csv"


# ── helpers ──────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _resolve_csv_path(dataset_key: str) -> Path | None:
    """Resolve 'raw/file.csv' or 'processed/file.csv' to a real Path."""
    parts = dataset_key.split("/", 1)
    if len(parts) != 2:
        return None
    source_dir, filename = parts
    if source_dir == "raw":
        return RAW_DATA_DIR / filename
    if source_dir == "processed":
        return PROCESSED_DATA_DIR / filename
    return None


def _get_disabled_source_filenames() -> set[str]:
    """Return set of raw base filenames (without extension) from disabled sources.

    Maps each disabled URL → its download filename stem so we can hide the
    corresponding datasets from the column configuration UI.
    Processed files often have prefixes (cleaned_, florida_) so we match
    on whether the dataset filename *contains* the raw stem.
    """
    import os
    from urllib.parse import urlparse

    state_file = CONFIG_DIR / "dataset_sources_state.json"
    if not state_file.exists():
        return set()
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return set()
    disabled_urls = state.get("disabled_urls", [])
    if not disabled_urls:
        return set()

    filenames: set[str] = set()
    for url in disabled_urls:
        parsed = urlparse(url)
        name = os.path.basename(parsed.path)
        if name:
            # Store the stem (without extension) for substring matching
            stem = os.path.splitext(name)[0]
            filenames.add(stem)
    return filenames


def _is_disabled_dataset(filename: str, disabled_stems: set[str]) -> bool:
    """Check if a dataset filename derives from a disabled source.

    Processed files are typically prefixed with cleaned_ or florida_, so
    we check if any disabled stem appears as a substring of the filename.
    """
    if not disabled_stems:
        return False
    name_no_ext = filename.rsplit(".", 1)[0] if "." in filename else filename
    for stem in disabled_stems:
        if stem in name_no_ext:
            return True
    return False


# ── GET /columns — merged column info ────────────────────────────

@bp.route("/columns", methods=["GET"])
def get_columns():
    """Return column config merged with data-dictionary metadata.

    Datasets whose source URL is disabled in the dashboard settings
    are silently omitted from the response.
    """
    col_config = _load_json(COLUMN_CONFIG)
    data_dict = _load_json(DATA_DICT)
    dd_datasets = data_dict.get("datasets", {})

    disabled_filenames = _get_disabled_source_filenames()

    result = {}
    total_cols = 0
    included_cols = 0

    # 1. Data-dictionary is the primary catalogue
    for ds_key, ds_info in dd_datasets.items():
        # Hide datasets from disabled sources
        parts = ds_key.split("/", 1)
        filename = parts[1] if len(parts) == 2 else ds_key
        if _is_disabled_dataset(filename, disabled_filenames):
            continue

        cc_entry = col_config.get(ds_key, {})
        cc_columns = cc_entry.get("columns", {})

        columns = {}
        for col_name, col_meta in ds_info.get("columns", {}).items():
            cc_col = cc_columns.get(col_name, {})
            include = cc_col.get("include", False)
            rename = cc_col.get("rename", None)

            columns[col_name] = {
                "dtype": col_meta.get("dtype", "unknown"),
                "include": include,
                "row_count": col_meta.get("non_null_count", 0),
                "total_rows": col_meta.get(
                    "total_rows",
                    col_meta.get("total_rows_scanned", 0),
                ),
                "rename": rename,
            }
            total_cols += 1
            if include:
                included_cols += 1

        result[ds_key] = {
            "source_dir": ds_info.get("source_dir", ""),
            "filename": filename,
            "columns": columns,
        }

    # 2. Include datasets in column_config but missing from dictionary
    for ds_key, ds_entry in col_config.items():
        if ds_key in result:
            continue
        # Hide datasets from disabled sources
        parts2 = ds_key.split("/", 1)
        fname2 = parts2[1] if len(parts2) == 2 else ds_key
        if _is_disabled_dataset(fname2, disabled_filenames):
            continue
        columns = {}
        for col_name, col_info in ds_entry.get("columns", {}).items():
            columns[col_name] = {
                "dtype": col_info.get("dtype", "unknown"),
                "include": col_info.get("include", False),
                "row_count": 0,
                "total_rows": 0,
                "rename": col_info.get("rename", None),
            }
            total_cols += 1
            if col_info.get("include"):
                included_cols += 1

        parts = ds_key.split("/", 1)
        filename = parts[1] if len(parts) == 2 else ds_key
        result[ds_key] = {
            "source_dir": parts[0] if len(parts) == 2 else "",
            "filename": filename,
            "columns": columns,
        }

    return jsonify({
        "datasets": result,
        "total_columns": total_cols,
        "included_columns": included_cols,
    })


# ── PUT /columns — batch include/exclude ─────────────────────────

@bp.route("/columns", methods=["PUT"])
def update_columns():
    """Batch update include/exclude status.

    Body: { "updates": [ { "dataset": "..", "column": "..", "include": bool } ] }
    """
    data = request.get_json(silent=True) or {}
    updates = data.get("updates", [])
    col_config = _load_json(COLUMN_CONFIG)

    for u in updates:
        ds = u.get("dataset", "")
        col = u.get("column", "")
        include = u.get("include", False)
        if not ds or not col:
            continue
        col_config.setdefault(ds, {}).setdefault("columns", {}).setdefault(col, {})
        col_config[ds]["columns"][col]["include"] = include

    _save_json(COLUMN_CONFIG, col_config)
    logger.info("Updated %d column(s)", len(updates))
    return jsonify({"status": "ok", "updated": len(updates)})


# ── PUT /columns/rename ──────────────────────────────────────────

@bp.route("/columns/rename", methods=["PUT"])
def rename_column():
    data = request.get_json(silent=True) or {}
    ds = data.get("dataset", "")
    col = data.get("column", "")
    new_name = data.get("newName", "").strip()

    if not ds or not col:
        return jsonify({"error": "dataset and column required"}), 400

    col_config = _load_json(COLUMN_CONFIG)
    col_config.setdefault(ds, {}).setdefault("columns", {}).setdefault(col, {})

    if new_name and new_name != col:
        col_config[ds]["columns"][col]["rename"] = new_name
    else:
        col_config[ds]["columns"][col].pop("rename", None)

    _save_json(COLUMN_CONFIG, col_config)
    logger.info("Renamed %s / %s → %s", ds, col, new_name or "(reset)")
    return jsonify({"status": "ok"})


# ── POST /columns/delete ─────────────────────────────────────────

@bp.route("/columns/delete", methods=["POST"])
def delete_columns():
    """Remove columns from config + data dictionary."""
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])

    col_config = _load_json(COLUMN_CONFIG)
    data_dict = _load_json(DATA_DICT)
    dd_datasets = data_dict.get("datasets", {})

    deleted = 0
    for item in items:
        ds = item.get("dataset", "")
        col = item.get("column", "")
        if ds in col_config and "columns" in col_config[ds]:
            if col_config[ds]["columns"].pop(col, None) is not None:
                deleted += 1
        if ds in dd_datasets and "columns" in dd_datasets[ds]:
            dd_datasets[ds]["columns"].pop(col, None)

    _save_json(COLUMN_CONFIG, col_config)
    if dd_datasets:
        data_dict["datasets"] = dd_datasets
        _save_json(DATA_DICT, data_dict)

    logger.info("Deleted %d column(s)", deleted)
    return jsonify({"status": "ok", "deleted": deleted})


# ── POST /columns/reset ──────────────────────────────────────────

@bp.route("/columns/reset", methods=["POST"])
def reset_columns():
    """Set every column to include=false and clear renames."""
    col_config = _load_json(COLUMN_CONFIG)
    for ds_entry in col_config.values():
        for col_info in ds_entry.get("columns", {}).values():
            col_info["include"] = False
            col_info.pop("rename", None)

    _save_json(COLUMN_CONFIG, col_config)
    logger.info("Reset all columns to excluded")
    return jsonify({"status": "ok"})


# ── POST /columns/scan ───────────────────────────────────────────

@bp.route("/columns/scan", methods=["POST"])
def scan_columns():
    """Re-scan datasets → data dictionary, then sync column_config."""
    try:
        from generate_data_dictionary import main as gen_dict
        dictionary = gen_dict()

        # Sync column_config: add new columns as excluded, keep existing
        col_config = _load_json(COLUMN_CONFIG)
        dd_datasets = dictionary.get("datasets", {})

        for ds_key, ds_info in dd_datasets.items():
            col_config.setdefault(ds_key, {}).setdefault("columns", {})
            for col_name in ds_info.get("columns", {}):
                if col_name not in col_config[ds_key]["columns"]:
                    col_config[ds_key]["columns"][col_name] = {"include": False}

        _save_json(COLUMN_CONFIG, col_config)

        total = sum(len(ds.get("columns", {})) for ds in dd_datasets.values())
        return jsonify({
            "status": "ok",
            "datasets": len(dd_datasets),
            "columns": total,
        })
    except Exception as exc:
        logger.error("Scan failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── POST /columns/rebuild — rebuild master_dataset.csv ───────────

@bp.route("/columns/rebuild", methods=["POST"])
def rebuild_master():
    """Rebuild master_dataset.csv from included columns only."""
    import pandas as pd

    col_config = _load_json(COLUMN_CONFIG)
    FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    loaded: list[str] = []

    for ds_key, ds_entry in col_config.items():
        columns_cfg = ds_entry.get("columns", {})
        included = [c for c, info in columns_cfg.items() if info.get("include")]
        if not included:
            continue

        csv_path = _resolve_csv_path(ds_key)
        if csv_path is None or not csv_path.exists():
            logger.warning("CSV not found for %s", ds_key)
            continue

        try:
            df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)
        except Exception as exc:
            logger.error("Error reading %s: %s", csv_path, exc)
            continue

        # Build rename map
        rename_map = {}
        for col, info in columns_cfg.items():
            rn = info.get("rename")
            if rn and col in df.columns:
                rename_map[col] = rn

        available = [c for c in included if c in df.columns]
        if not available:
            continue

        df = df[available].copy()
        if rename_map:
            df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

        df.insert(0, "_source_dataset", Path(ds_key).stem)
        frames.append(df)
        loaded.append(ds_key)

    if frames:
        master = pd.concat(frames, ignore_index=True, sort=False)
    else:
        master = pd.DataFrame()

    master.to_csv(MASTER_CSV, index=False, encoding="utf-8")

    rows = len(master)
    cols = len(master.columns)
    logger.info("Rebuilt master_dataset: %d rows × %d cols from %d datasets",
                rows, cols, len(loaded))
    return jsonify({
        "status": "ok",
        "rows": rows,
        "columns": cols,
        "datasets_used": len(loaded),
    })


# ── GET /master — paginated master_dataset viewer ────────────────

@bp.route("/master", methods=["GET"])
def get_master():
    if not MASTER_CSV.exists():
        return jsonify({
            "columns": [], "rows": [], "totalRows": 0,
            "page": 1, "totalPages": 0, "totalColumns": 0,
        })

    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 100, type=int)
    page_size = min(page_size, 500)

    try:
        import pandas as pd

        df = pd.read_csv(MASTER_CSV, encoding="utf-8", low_memory=False)
        total_rows = len(df)

        if total_rows == 0:
            return jsonify({
                "columns": list(df.columns), "rows": [],
                "totalRows": 0, "page": 1, "totalPages": 0,
                "totalColumns": len(df.columns),
            })

        total_pages = max(1, -(-total_rows // page_size))   # ceil div
        page = max(1, min(page, total_pages))

        start = (page - 1) * page_size
        page_df = df.iloc[start : start + page_size]

        # JSON-safe serialisation (handles NaN, numpy types)
        rows = json.loads(page_df.to_json(orient="values"))

        return jsonify({
            "columns": list(df.columns),
            "rows": rows,
            "totalRows": total_rows,
            "totalColumns": len(df.columns),
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages,
        })
    except Exception as exc:
        logger.error("Error reading master dataset: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── GET /master/info ──────────────────────────────────────────────

@bp.route("/master/info", methods=["GET"])
def master_info():
    if not MASTER_CSV.exists():
        return jsonify({"exists": False, "rows": 0, "columns": 0})
    try:
        with open(MASTER_CSV, "r", encoding="utf-8") as fh:
            header = next(csv.reader(fh), [])
            row_count = sum(1 for _ in fh)
        return jsonify({
            "exists": True,
            "rows": row_count,
            "columns": len(header),
            "column_names": header,
            "size_bytes": MASTER_CSV.stat().st_size,
        })
    except Exception as exc:
        return jsonify({"exists": False, "error": str(exc)})
