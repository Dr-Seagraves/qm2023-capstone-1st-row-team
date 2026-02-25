"""
Build Master Dataset
====================

Combines the Filter + Merge steps into a single automated pipeline stage.
1. Filters Zillow data to Florida MSAs (if not already filtered)
2. Runs hurricane filter scripts
3. Runs specialized merge scripts
4. Builds master_dataset.csv from **only the columns the user has
   marked as "include" in config/column_config.json**

By default, master_dataset.csv is EMPTY until the user selects columns
in the dashboard's Settings → Column Configuration tab.

This replaces the old separate filter_all.py + merge_all.py pipeline.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from config_paths import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    FINAL_DATA_DIR,
    CONFIG_DIR,
    LOGS_DIR,
)
from logging_config import setup_logger

logger = setup_logger("build.master")

# Zillow metadata columns (not date values)
ZILLOW_META = {"RegionID", "SizeRank", "RegionName", "RegionType", "StateName"}


# ---- Step 1: Filter raw Zillow CSVs to Florida MSAs ----

def filter_zillow_to_florida() -> list[Path]:
    """Filter raw Zillow Metro_*.csv to Florida MSAs → data/processed/florida_*."""
    output_files: list[Path] = []

    for csv_path in sorted(RAW_DATA_DIR.glob("Metro_*.csv")):
        output_name = f"florida_{csv_path.name}"
        output_path = PROCESSED_DATA_DIR / output_name

        # Skip if already filtered and newer than source
        if output_path.exists() and output_path.stat().st_mtime >= csv_path.stat().st_mtime:
            output_files.append(output_path)
            continue

        logger.info("  Filtering %s → %s", csv_path.name, output_name)
        florida_rows = 0
        try:
            with open(csv_path, "r", encoding="utf-8") as fin:
                reader = csv.DictReader(fin)
                if reader.fieldnames is None:
                    continue
                with open(output_path, "w", newline="", encoding="utf-8") as fout:
                    writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    for row in reader:
                        if row.get("StateName") == "FL" and row.get("RegionType") == "msa":
                            writer.writerow(row)
                            florida_rows += 1
        except Exception as exc:
            logger.error("  Error filtering %s: %s", csv_path.name, exc)
            continue

        if florida_rows > 0:
            output_files.append(output_path)
            logger.info("    %d Florida MSA rows", florida_rows)
        else:
            output_path.unlink(missing_ok=True)

    return output_files


# ---- Step 2: Run existing filter scripts for hurricane data ----

def run_filter_scripts() -> None:
    """Execute the hurricane filter scripts that produce data/processed/ files."""
    import subprocess

    filter_dir = Path(__file__).resolve().parent.parent / "filter"
    scripts = [
        # "filter_florida_storms_60nm.py",  # Requires HURDAT2 data (URL unavailable)
        # "filter_florida_landfall_hurricanes.py",  # Requires HURDAT2 data
    ]

    for script_name in scripts:
        script_path = filter_dir / script_name
        if not script_path.exists():
            logger.warning("  Filter script not found: %s", script_name)
            continue
        logger.info("  Running %s ...", script_name)
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode != 0:
                logger.error("  FAILED %s: %s", script_name, result.stderr[-500:])
        except Exception as exc:
            logger.error("  ERROR %s: %s", script_name, exc)


# ---- Step 3: Run merge scripts for hurricane-economic data ----

def run_merge_scripts() -> None:
    """Execute specialized merge scripts (hurricane+economic, zillow metrics)."""
    import subprocess

    merge_dir = Path(__file__).resolve().parent.parent / "merge"
    scripts = [
        "merge_hurricane_economic.py",
        "merge_zillow_metrics.py",
    ]

    for script_name in scripts:
        script_path = merge_dir / script_name
        if not script_path.exists():
            logger.warning("  Merge script not found: %s", script_name)
            continue
        logger.info("  Running %s ...", script_name)
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode != 0:
                logger.error("  FAILED %s: %s", script_name, result.stderr[-500:])
        except Exception as exc:
            logger.error("  ERROR %s: %s", script_name, exc)


# ---- Step 4: Build master_dataset.csv from included columns ----

def _resolve_csv_path(dataset_key: str) -> Path | None:
    """Turn 'raw/file.csv' or 'processed/file.csv' into an actual Path."""
    parts = dataset_key.split("/", 1)
    if len(parts) != 2:
        return None
    source_dir, filename = parts
    if source_dir == "raw":
        return RAW_DATA_DIR / filename
    if source_dir == "processed":
        return PROCESSED_DATA_DIR / filename
    return None


def build_master_dataset() -> Path | None:
    """
    Build master_dataset.csv using **only** the columns marked as
    ``include: true`` in config/column_config.json.

    If column_config.json does not exist or no columns are included,
    an empty CSV is written (the user hasn't selected anything yet).
    """
    import json

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = FINAL_DATA_DIR / "master_dataset.csv"
    col_config_path = CONFIG_DIR / "column_config.json"

    if not col_config_path.exists():
        logger.info("  No column_config.json — writing empty master_dataset.csv")
        pd.DataFrame().to_csv(output_path, index=False, encoding="utf-8")
        return output_path

    col_config: dict = json.loads(col_config_path.read_text(encoding="utf-8"))

    frames: list[pd.DataFrame] = []
    loaded: list[str] = []

    for ds_key, ds_entry in col_config.items():
        columns_cfg = ds_entry.get("columns", {})
        included = [c for c, info in columns_cfg.items() if info.get("include")]
        if not included:
            continue

        csv_path = _resolve_csv_path(ds_key)
        if csv_path is None or not csv_path.exists():
            logger.warning("  CSV not found for %s", ds_key)
            continue

        logger.info("  Loading %s (%d included cols)", csv_path.name, len(included))
        try:
            df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)
        except Exception as exc:
            logger.error("  Error reading %s: %s", csv_path.name, exc)
            continue

        # Apply renames stored in column_config
        rename_map = {
            col: info["rename"]
            for col, info in columns_cfg.items()
            if info.get("rename") and col in df.columns
        }

        available = [c for c in included if c in df.columns]
        if not available:
            continue

        df = df[available].copy()
        if rename_map:
            df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

        df.insert(0, "_source_dataset", csv_path.stem)
        frames.append(df)
        loaded.append(csv_path.name)
        logger.info("    %d rows × %d cols", len(df), len(df.columns))

    if frames:
        master = pd.concat(frames, ignore_index=True, sort=False)
    else:
        master = pd.DataFrame()
        logger.info("  No included columns — master_dataset.csv will be empty")

    master.to_csv(output_path, index=False, encoding="utf-8")

    logger.info("=" * 50)
    logger.info("master_dataset.csv: %d rows × %d cols", len(master), len(master.columns))
    if loaded:
        logger.info("Source datasets: %s", ", ".join(loaded))

    return output_path


# ---- Main entry point ----

def main() -> None:
    logger.info("=" * 60)
    logger.info("BUILD MASTER DATASET")
    logger.info("  Filter + Merge + Build (automated)")
    logger.info("=" * 60)

    logger.info("[1/4] Filtering Zillow data to Florida MSAs...")
    filtered = filter_zillow_to_florida()
    logger.info("  %d Zillow files ready", len(filtered))

    logger.info("[2/4] Running hurricane filters...")
    run_filter_scripts()

    logger.info("[3/4] Running specialized merges...")
    run_merge_scripts()

    logger.info("[4/4] Building master_dataset.csv (included columns only)...")
    result = build_master_dataset()

    if result:
        logger.info("BUILD COMPLETE: %s", result)
    else:
        logger.error("BUILD FAILED — no output produced")


if __name__ == "__main__":
    main()