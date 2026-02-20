"""
Merge All — reads config/merge_config.json, selects columns from each
enabled dataset, and concatenates them into data/final/master_dataset.csv.

The merge config is editable from:
  1. The file  config/merge_config.json  (for CLI / version-control)
  2. The dashboard  Settings > Merge Configuration  (via /api/merge/config)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import CONFIG_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, FINAL_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("merge.all")

CONFIG_FILE = CONFIG_DIR / "merge_config.json"

DIR_MAP = {
    "processed": PROCESSED_DATA_DIR,
    "raw": RAW_DATA_DIR,
    "final": FINAL_DATA_DIR,
}


def load_merge_config() -> dict:
    """Load merge configuration from config/merge_config.json."""
    if not CONFIG_FILE.exists():
        logger.error("Merge config not found: %s", CONFIG_FILE)
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    logger.info("=" * 60)
    logger.info("MERGE ALL DATA  -->  data/final/master_dataset.csv")
    logger.info("=" * 60)

    config = load_merge_config()
    if not config:
        logger.error("Empty or missing merge config. Aborting.")
        return

    output_name = config.get("output_filename", "master_dataset.csv")
    datasets_cfg = config.get("datasets", {})

    frames: list[pd.DataFrame] = []
    loaded_names: list[str] = []

    for ds_key, ds_info in datasets_cfg.items():
        if not ds_info.get("enabled", False):
            logger.info("  SKIP (disabled): %s", ds_key)
            continue

        filename = ds_info.get("filename", "")
        directory = ds_info.get("directory", "processed")
        selected_columns = ds_info.get("columns", [])

        base_dir = DIR_MAP.get(directory, PROCESSED_DATA_DIR)
        csv_path = base_dir / filename

        if not csv_path.exists():
            logger.warning("  NOT FOUND: %s — skipping %s", csv_path, ds_key)
            continue

        logger.info("  Loading %s  (%s)", ds_key, csv_path.name)

        try:
            df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)
        except Exception as exc:
            logger.error("  ERROR reading %s: %s", csv_path, exc)
            continue

        # Keep only the columns the user selected (if any were specified)
        if selected_columns:
            available = [c for c in selected_columns if c in df.columns]
            missing = [c for c in selected_columns if c not in df.columns]
            if missing:
                logger.warning("    Columns not found in %s: %s", ds_key, missing)
            df = df[available]

        # Tag rows with their source dataset
        df.insert(0, "_source_dataset", ds_key)

        frames.append(df)
        loaded_names.append(ds_key)
        logger.info("    -> %d rows, %d columns", len(df), len(df.columns))

    if not frames:
        logger.error("No datasets loaded. master_dataset will not be created.")
        return

    # Concatenate all DataFrames (missing columns filled with NaN)
    master = pd.concat(frames, ignore_index=True, sort=False)

    # Write to data/final/
    FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FINAL_DATA_DIR / output_name
    master.to_csv(output_path, index=False, encoding="utf-8")

    logger.info("-" * 60)
    logger.info("master_dataset written to %s", output_path)
    logger.info("  Datasets merged: %s", ", ".join(loaded_names))
    logger.info("  Total rows: %d   Total columns: %d", len(master), len(master.columns))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
