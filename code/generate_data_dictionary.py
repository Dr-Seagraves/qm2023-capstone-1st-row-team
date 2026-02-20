"""
Generate Data Dictionary
=========================

Scans all CSV files in data/raw/ and data/processed/, extracts column metadata,
and writes:
  data/final/data_dictionary.json  (source of truth)
  data/final/data_dictionary.csv   (flattened export)

Can be run standalone or called from the dashboard.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR, FINAL_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("general.data_dictionary")

OUTPUT_JSON = FINAL_DATA_DIR / "data_dictionary.json"
OUTPUT_CSV = FINAL_DATA_DIR / "data_dictionary.csv"

MAX_SAMPLE_VALUES = 5
MAX_ROWS_SCAN = 500  # scan first N rows for type inference


def infer_dtype(values: list[str]) -> str:
    """Infer a simple dtype from a list of string values."""
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return "unknown"

    # Try int
    int_count = 0
    float_count = 0
    date_count = 0
    for v in non_empty[:50]:
        try:
            int(v)
            int_count += 1
            continue
        except ValueError:
            pass
        try:
            float(v)
            float_count += 1
            continue
        except ValueError:
            pass
        # Simple date heuristic: contains '-' and digits
        if len(v) >= 8 and "-" in v:
            parts = v.split("-")
            if len(parts) in (2, 3) and all(p.isdigit() for p in parts):
                date_count += 1

    total = len(non_empty[:50])
    if int_count == total:
        return "integer"
    if (int_count + float_count) == total:
        return "float"
    if date_count > total * 0.8:
        return "date"
    return "string"


def _count_file_rows(csv_path: Path) -> int:
    """Fast total-row count (excludes header)."""
    try:
        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            return max(0, sum(1 for _ in f) - 1)
    except Exception:
        return 0


def scan_csv(csv_path: Path) -> dict:
    """Scan a CSV and return column metadata."""
    columns: dict[str, dict] = {}

    # Quick full row count (fast line iteration, no CSV parsing)
    file_total_rows = _count_file_rows(csv_path)

    try:
        with open(csv_path, "r", encoding="utf-8", errors="replace") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames:
                return columns

            col_values: dict[str, list[str]] = {col: [] for col in reader.fieldnames}
            null_counts: dict[str, int] = {col: 0 for col in reader.fieldnames}
            scanned_rows = 0

            for i, row in enumerate(reader):
                if i >= MAX_ROWS_SCAN:
                    break
                scanned_rows += 1
                for col in reader.fieldnames:
                    val = row.get(col, "")
                    if val.strip():
                        col_values[col].append(val.strip())
                    else:
                        null_counts[col] += 1

            for col in reader.fieldnames:
                vals = col_values[col]
                columns[col] = {
                    "dtype": infer_dtype(vals),
                    "description": "",
                    "nullable": null_counts[col] > 0,
                    "non_null_count": scanned_rows - null_counts[col],
                    "total_rows_scanned": scanned_rows,
                    "total_rows": file_total_rows,
                    "sample_values": vals[:MAX_SAMPLE_VALUES],
                    "include": False,
                }

    except Exception as exc:
        logger.error("Error scanning %s: %s", csv_path.name, exc)

    return columns


def generate() -> dict:
    """Scan all CSVs and build the data dictionary."""
    dictionary: dict = {
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "datasets": {},
    }

    scan_dirs = [
        ("raw", RAW_DATA_DIR),
        ("processed", PROCESSED_DATA_DIR),
    ]

    for label, dir_path in scan_dirs:
        if not dir_path.exists():
            continue
        for csv_path in sorted(dir_path.glob("*.csv")):
            logger.info("Scanning %s/%s ...", label, csv_path.name)
            columns = scan_csv(csv_path)
            if columns:
                key = f"{label}/{csv_path.name}"
                dictionary["datasets"][key] = {
                    "source_dir": label,
                    "filename": csv_path.name,
                    "description": "",
                    "columns": columns,
                }

    return dictionary


def export_csv(dictionary: dict) -> None:
    """Export flattened data dictionary to CSV."""
    rows: list[dict] = []
    for dataset_key, ds_info in dictionary.get("datasets", {}).items():
        for col_name, col_info in ds_info.get("columns", {}).items():
            rows.append({
                "Dataset": dataset_key,
                "Column": col_name,
                "Type": col_info.get("dtype", ""),
                "Description": col_info.get("description", ""),
                "Nullable": col_info.get("nullable", ""),
                "NonNullCount": col_info.get("non_null_count", ""),
                "SampleValues": "; ".join(str(v) for v in col_info.get("sample_values", [])),
                "Include": col_info.get("include", True),
            })

    fieldnames = ["Dataset", "Column", "Type", "Description", "Nullable",
                  "NonNullCount", "SampleValues", "Include"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Exported CSV dictionary: %s (%d entries)", OUTPUT_CSV, len(rows))


def main() -> dict:
    logger.info("Generating data dictionary...")

    # If JSON already exists, preserve user-edited descriptions
    existing_descriptions: dict[str, dict[str, str]] = {}
    if OUTPUT_JSON.exists():
        try:
            existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
            for ds_key, ds_info in existing.get("datasets", {}).items():
                for col_name, col_info in ds_info.get("columns", {}).items():
                    desc = col_info.get("description", "")
                    if desc:
                        existing_descriptions.setdefault(ds_key, {})[col_name] = desc
        except Exception:
            pass

    dictionary = generate()

    # Re-apply preserved descriptions
    for ds_key, col_descs in existing_descriptions.items():
        if ds_key in dictionary["datasets"]:
            for col_name, desc in col_descs.items():
                if col_name in dictionary["datasets"][ds_key]["columns"]:
                    dictionary["datasets"][ds_key]["columns"][col_name]["description"] = desc

    # Write JSON
    FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(dictionary, fh, indent=2, ensure_ascii=False)
    logger.info("Wrote data dictionary JSON: %s", OUTPUT_JSON)

    # Write CSV export
    export_csv(dictionary)

    dataset_count = len(dictionary["datasets"])
    col_count = sum(len(ds["columns"]) for ds in dictionary["datasets"].values())
    logger.info("Data dictionary: %d datasets, %d total columns", dataset_count, col_count)

    return dictionary


if __name__ == "__main__":
    main()
