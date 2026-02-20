"""
Clean Zillow Data
=================

Cleans all Zillow-related CSVs found in RAW_DATA_DIR.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR
from logging_config import setup_logger
from clean.clean_utils import (
    standardize_column_names,
    drop_empty_rows,
    fix_dtypes,
    generate_cleaning_report,
    ensure_wide_format,
)

logger = setup_logger("clean.zillow")

# Patterns that identify a Zillow file (case-insensitive)
_ZILLOW_PAT = re.compile(r"zillow|zhvi|zori|Metro_", re.IGNORECASE)
# Pattern for date-like column names  (e.g. "2020-01-31")
_DATE_COL_PAT = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _clean_one(csv_path: Path) -> None:
    """Clean a single Zillow CSV and save to PROCESSED_DATA_DIR."""
    logger.info("Cleaning %s", csv_path.name)

    df_raw = pd.read_csv(csv_path, low_memory=False)
    df = df_raw.copy()

    # 1. Standardize column names
    df = standardize_column_names(df)

    # 2. Drop mostly-empty rows
    df = drop_empty_rows(df, threshold=0.6)

    # 3. Auto-fix dtypes
    df = fix_dtypes(df)

    # 4. Ensure date-like column names are stored as float
    for col in df.columns:
        if _DATE_COL_PAT.match(col):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Ensure wide format (validate / convert if accidentally long)
    df = ensure_wide_format(df)

    # 6. Report
    report = generate_cleaning_report(df_raw, df, csv_path.name)
    logger.info(
        "  %s -- rows: %d->%d (-%d), nulls remaining: %d cols",
        csv_path.name,
        report["rows_before"],
        report["rows_after"],
        report["rows_dropped"],
        len(report["null_summary"]),
    )

    # 7. Save
    out_path = PROCESSED_DATA_DIR / f"cleaned_{csv_path.name}"
    df.to_csv(out_path, index=False)
    logger.info("  Saved → %s", out_path.name)


def main() -> None:
    logger.info("=" * 60)
    logger.info("CLEAN ZILLOW DATA")
    logger.info("=" * 60)

    csv_files = [
        f
        for f in sorted(RAW_DATA_DIR.glob("*.csv"))
        if _ZILLOW_PAT.search(f.name)
    ]

    if not csv_files:
        logger.warning("No Zillow CSVs found in %s", RAW_DATA_DIR)
        return

    logger.info("Found %d Zillow CSV(s)", len(csv_files))

    for csv_path in csv_files:
        try:
            _clean_one(csv_path)
        except Exception as exc:
            logger.error("Failed to clean %s: %s", csv_path.name, exc)

    logger.info("Zillow cleaning complete.")


if __name__ == "__main__":
    main()
