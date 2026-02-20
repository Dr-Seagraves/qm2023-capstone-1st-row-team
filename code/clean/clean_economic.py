"""
Clean Economic Impact Data
===========================

Cleans hurricane economic impact CSVs found in RAW_DATA_DIR or PROCESSED_DATA_DIR.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
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

logger = setup_logger("clean.economic")

_ECON_PAT = re.compile(r"hurricane_economic|economic", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Dollar-string parsing
# ---------------------------------------------------------------------------

_DOLLAR_STRIP = re.compile(r"[\$,]")
_BILLION = re.compile(r"([\d.]+)\s*billion", re.IGNORECASE)
_MILLION = re.compile(r"([\d.]+)\s*million", re.IGNORECASE)


def _parse_dollar(value) -> float | None:
    """Convert dollar strings like '$1.5 Billion' → 1_500_000_000.0."""
    if pd.isna(value):
        return np.nan

    s = str(value).strip()
    if s == "":
        return np.nan

    m = _BILLION.search(s)
    if m:
        return float(m.group(1)) * 1e9

    m = _MILLION.search(s)
    if m:
        return float(m.group(1)) * 1e6

    # Strip $ and commas, try plain numeric
    cleaned = _DOLLAR_STRIP.sub("", s)
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def _parse_dollar_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect and convert columns that contain dollar-formatted values."""
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().head(30).astype(str)
        if sample.empty:
            continue
        # If a significant share look like dollar amounts, convert
        dollar_like = sample.str.contains(r"\$|billion|million", case=False, na=False)
        if dollar_like.mean() > 0.3:
            df[col] = df[col].apply(_parse_dollar)
            logger.info("  Parsed dollar column: %s", col)
    return df


def _normalize_storm_names(df: pd.DataFrame) -> pd.DataFrame:
    """Title-case and strip whitespace from storm name columns."""
    df = df.copy()
    name_cols = [c for c in df.columns if "name" in c.lower()]
    for col in name_cols:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].str.strip().str.title()
    return df


def _find_economic_csvs() -> list[Path]:
    """Return deduplicated list of economic CSV paths from both dirs."""
    seen: set[str] = set()
    results: list[Path] = []
    for directory in (RAW_DATA_DIR, PROCESSED_DATA_DIR):
        for f in sorted(directory.glob("*.csv")):
            if _ECON_PAT.search(f.name) and f.name not in seen:
                seen.add(f.name)
                results.append(f)
    return results


def _clean_one(csv_path: Path) -> None:
    logger.info("Cleaning %s", csv_path.name)

    df_raw = pd.read_csv(csv_path, low_memory=False)
    df = df_raw.copy()

    # 1. Column names
    df = standardize_column_names(df)

    # 2. Dollar amounts
    df = _parse_dollar_columns(df)

    # 3. Types
    df = fix_dtypes(df)

    # 4. Empty rows
    df = drop_empty_rows(df, threshold=0.5)

    # 5. Storm names
    df = _normalize_storm_names(df)

    # 6. Ensure wide format
    df = ensure_wide_format(df)

    # 7. Report
    report = generate_cleaning_report(df_raw, df, csv_path.name)
    logger.info(
        "  %s — rows: %d→%d (-%d)",
        csv_path.name,
        report["rows_before"],
        report["rows_after"],
        report["rows_dropped"],
    )

    # 7. Save
    out_path = PROCESSED_DATA_DIR / f"cleaned_{csv_path.name}"
    df.to_csv(out_path, index=False)
    logger.info("  Saved → %s", out_path.name)


def main() -> None:
    logger.info("=" * 60)
    logger.info("CLEAN ECONOMIC DATA")
    logger.info("=" * 60)

    csv_files = _find_economic_csvs()

    if not csv_files:
        logger.warning("No economic CSVs found in %s or %s", RAW_DATA_DIR, PROCESSED_DATA_DIR)
        return

    logger.info("Found %d economic CSV(s)", len(csv_files))

    for csv_path in csv_files:
        try:
            _clean_one(csv_path)
        except Exception as exc:
            logger.error("Failed to clean %s: %s", csv_path.name, exc)

    logger.info("Economic cleaning complete.")


if __name__ == "__main__":
    main()
