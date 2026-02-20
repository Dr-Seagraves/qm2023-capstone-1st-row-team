"""
Shared Cleaning Utilities
=========================

Reusable helper functions used by every clean_*.py script.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logging_config import setup_logger

logger = setup_logger("clean.utils")


# ---------------------------------------------------------------------------
# check_missing_values
# ---------------------------------------------------------------------------

def check_missing_values(df: pd.DataFrame) -> dict:
    """Return a dict {col_name: {count, pct}} for columns with any nulls."""
    missing: dict = {}
    for col in df.columns:
        n_null = int(df[col].isna().sum())
        if n_null > 0:
            missing[col] = {
                "count": n_null,
                "pct": round(n_null / len(df) * 100, 2) if len(df) > 0 else 0.0,
            }
    return missing


# ---------------------------------------------------------------------------
# detect_outliers_iqr
# ---------------------------------------------------------------------------

def detect_outliers_iqr(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    factor: float = 1.5,
) -> pd.DataFrame:
    """Return a boolean DataFrame (True = outlier) for numeric columns using IQR."""
    if columns is None:
        columns = df.select_dtypes(include="number").columns.tolist()
    else:
        columns = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]

    outlier_mask = pd.DataFrame(False, index=df.index, columns=columns)
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        outlier_mask[col] = (df[col] < lower) | (df[col] > upper)
    return outlier_mask


# ---------------------------------------------------------------------------
# fix_dtypes
# ---------------------------------------------------------------------------

_DATE_PATTERN = re.compile(
    r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}"  # e.g. 2024-01-15 …
)


def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Auto-convert object columns that look numeric or date-like."""
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        # Try numeric first
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0.5 * df[col].notna().sum():
            df[col] = converted
            continue

        # Try date-like
        sample = df[col].dropna().head(20).astype(str)
        if sample.empty:
            continue
        if sample.apply(lambda v: bool(_DATE_PATTERN.match(v))).mean() > 0.5:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass
    return df


# ---------------------------------------------------------------------------
# standardize_column_names
# ---------------------------------------------------------------------------

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip whitespace, replace spaces with underscores."""
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_") for c in df.columns
    ]
    return df


# ---------------------------------------------------------------------------
# drop_empty_rows
# ---------------------------------------------------------------------------

def drop_empty_rows(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Drop rows where more than *threshold* fraction of values are null."""
    if len(df.columns) == 0:
        return df
    min_non_null = int((1 - threshold) * len(df.columns))
    return df.dropna(thresh=max(min_non_null, 1)).reset_index(drop=True)


# ---------------------------------------------------------------------------
# generate_cleaning_report
# ---------------------------------------------------------------------------

def generate_cleaning_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    dataset_name: str,
) -> dict:
    """Return a summary dict describing what changed during cleaning."""
    null_summary = check_missing_values(df_after)
    outlier_summary: dict = {}
    try:
        outlier_mask = detect_outliers_iqr(df_after)
        for col in outlier_mask.columns:
            n = int(outlier_mask[col].sum())
            if n > 0:
                outlier_summary[col] = n
    except Exception:
        pass

    return {
        "dataset_name": dataset_name,
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_dropped": len(df_before) - len(df_after),
        "columns_cleaned": list(df_after.columns),
        "null_summary": null_summary,
        "outlier_summary": outlier_summary,
    }


# ---------------------------------------------------------------------------
# ensure_wide_format
# ---------------------------------------------------------------------------

_DATE_COL = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def detect_format(df: pd.DataFrame) -> str:
    """Detect if a DataFrame is in wide or long format.

    Heuristic: if many columns look like dates (YYYY-MM or YYYY-MM-DD),
    it is wide format.  If there are columns like 'date' / 'period' / 'value'
    it is likely long format.
    """
    date_col_count = sum(1 for c in df.columns if _DATE_COL.match(str(c)))
    if date_col_count > 5:
        return "wide"

    lower_cols = [str(c).lower() for c in df.columns]
    long_indicators = {"date", "period", "month", "year", "value", "metric"}
    if len(long_indicators & set(lower_cols)) >= 2 and date_col_count == 0:
        return "long"

    return "wide"  # default assumption


def ensure_wide_format(
    df: pd.DataFrame,
    id_cols: list[str] | None = None,
    date_col: str | None = None,
    value_col: str | None = None,
) -> pd.DataFrame:
    """Convert a long-format DataFrame to wide format if necessary.

    Parameters
    ----------
    df : DataFrame to check/convert.
    id_cols : Columns that identify each row-group (e.g. RegionName).
              If None, auto-detected as non-date, non-value columns.
    date_col : Column holding dates (e.g. 'date', 'period').
    value_col : Column holding the metric value.

    Returns the DataFrame in wide format (unchanged if already wide).
    """
    fmt = detect_format(df)
    if fmt == "wide":
        logger.info("  Data is already in wide format (%d date columns detected)",
                     sum(1 for c in df.columns if _DATE_COL.match(str(c))))
        return df

    # --- Auto-detect columns if not provided ---
    lower_map = {str(c).lower(): c for c in df.columns}

    if date_col is None:
        for candidate in ("date", "period", "month", "year_month"):
            if candidate in lower_map:
                date_col = lower_map[candidate]
                break
    if value_col is None:
        for candidate in ("value", "metric_value", "amount"):
            if candidate in lower_map:
                value_col = lower_map[candidate]
                break

    if date_col is None or value_col is None:
        logger.warning("  Cannot auto-detect long-format columns; skipping pivot")
        return df

    if id_cols is None:
        id_cols = [c for c in df.columns if c != date_col and c != value_col]

    logger.info("  Pivoting long → wide: date=%s, value=%s, ids=%s",
                date_col, value_col, id_cols[:3])

    try:
        wide = df.pivot_table(
            index=id_cols, columns=date_col, values=value_col, aggfunc="first"
        ).reset_index()
        wide.columns.name = None
        # Flatten MultiIndex columns if present
        wide.columns = [
            str(c) if not isinstance(c, tuple) else "_".join(str(x) for x in c)
            for c in wide.columns
        ]
        logger.info("  Pivoted to wide: %d rows x %d cols", len(wide), len(wide.columns))
        return wide
    except Exception as exc:
        logger.warning("  Pivot failed: %s — returning original", exc)
        return df
