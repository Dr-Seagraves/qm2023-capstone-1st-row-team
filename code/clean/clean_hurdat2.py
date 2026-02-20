"""
Clean HURDAT2 Data
==================

Parses the HURDAT2 fixed-width text format into a tidy CSV.
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

logger = setup_logger("clean.hurdat2")

# Header lines start with basin codes
_HEADER_PAT = re.compile(r"^(AL|EP|CP)")


def _find_hurdat_file() -> Path | None:
    """Locate the HURDAT2 source file in RAW_DATA_DIR."""
    candidate = RAW_DATA_DIR / "hurdat2_sample.txt"
    if candidate.exists():
        return candidate
    matches = sorted(RAW_DATA_DIR.glob("hurdat*"))
    return matches[0] if matches else None


def _parse_lat(raw: str) -> float:
    """Convert '28.0N' / '15.5S' → signed float."""
    raw = raw.strip()
    if not raw or raw == "":
        return np.nan
    sign = -1 if raw[-1] in ("S", "s") else 1
    try:
        return sign * float(raw[:-1])
    except ValueError:
        return np.nan


def _parse_lon(raw: str) -> float:
    """Convert '80.0W' / '120.5E' → signed float (W is negative)."""
    raw = raw.strip()
    if not raw or raw == "":
        return np.nan
    sign = -1 if raw[-1] in ("W", "w") else 1
    try:
        return sign * float(raw[:-1])
    except ValueError:
        return np.nan


def _parse_hurdat2(filepath: Path) -> pd.DataFrame:
    """Read a HURDAT2 text file and return a tidy DataFrame."""
    records: list[dict] = []
    current_id: str = ""
    current_name: str = ""

    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            parts = [p.strip() for p in line.split(",")]

            # --- header line ---
            if _HEADER_PAT.match(parts[0]):
                current_id = parts[0]
                current_name = parts[1] if len(parts) > 1 else ""
                continue

            # --- data line (expect at least 8 fields) ---
            if len(parts) < 8:
                continue

            try:
                date_str = parts[0]  # YYYYMMDD
                time_str = parts[1]  # HHMM
                record_type = parts[2]
                lat = _parse_lat(parts[3])
                lon = _parse_lon(parts[4])
                max_wind = pd.to_numeric(parts[5], errors="coerce")
                min_pressure = pd.to_numeric(parts[6], errors="coerce")

                # Additional wind radii (34/50/64 kt) may be in remaining fields
                extra = {f"field_{i}": parts[i] for i in range(7, len(parts))}

                record = {
                    "storm_id": current_id,
                    "name": current_name,
                    "date": date_str,
                    "time": time_str,
                    "record_type": record_type,
                    "lat": lat,
                    "lon": lon,
                    "max_wind": max_wind,
                    "min_pressure": min_pressure,
                    **extra,
                }
                records.append(record)
            except Exception:
                continue

    df = pd.DataFrame(records)
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning rules to the parsed DataFrame."""
    df = df.copy()

    # Replace sentinel missing values
    for col in ("max_wind", "min_pressure"):
        if col in df.columns:
            df[col] = df[col].replace([-999, -99, -999.0, -99.0], np.nan)

    # Ensure lat/lon are float (already handled in parsing, but just in case)
    for col in ("lat", "lon"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    return df


def main() -> None:
    logger.info("=" * 60)
    logger.info("CLEAN HURDAT2 DATA")
    logger.info("=" * 60)

    filepath = _find_hurdat_file()
    if filepath is None:
        logger.warning("No HURDAT2 file found in %s", RAW_DATA_DIR)
        return

    logger.info("Reading %s", filepath.name)

    try:
        df = _parse_hurdat2(filepath)
        logger.info("Parsed %d records from %s", len(df), filepath.name)

        df = _clean(df)

        out_path = PROCESSED_DATA_DIR / "cleaned_hurdat2.csv"
        df.to_csv(out_path, index=False)
        logger.info("Saved → %s  (%d rows, %d cols)", out_path.name, len(df), len(df.columns))
    except Exception as exc:
        logger.error("Failed to clean HURDAT2: %s", exc)

    logger.info("HURDAT2 cleaning complete.")


if __name__ == "__main__":
    main()
