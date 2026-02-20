"""
Merge hurricane track data with economic impact data.

Reads:
  data/processed/florida_storms_60nm_summary.csv
  data/processed/hurricane_economic_impacts_1980_2024_florida_landfall.csv
Writes:
  data/processed/florida_hurricane_economic_merged.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import PROCESSED_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("merge.hurricane_economic")

TRACK_CSV = PROCESSED_DATA_DIR / "florida_storms_60nm_summary.csv"
ECON_CSV = PROCESSED_DATA_DIR / "hurricane_economic_impacts_1980_2024_florida_landfall.csv"
OUTPUT_CSV = PROCESSED_DATA_DIR / "florida_hurricane_economic_merged.csv"


def load_track_data() -> dict[tuple[str, int], dict]:
    """Load storm track summary keyed by (STORM_NAME_UPPER, year)."""
    data: dict[tuple[str, int], dict] = {}
    if not TRACK_CSV.exists():
        logger.warning("Track CSV not found: %s", TRACK_CSV)
        return data

    with open(TRACK_CSV, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            name = row.get("Storm", "").strip().upper()
            year = int(row.get("Year", 0))
            if name and year:
                data[(name, year)] = row
    return data


def load_econ_data() -> list[dict]:
    """Load economic impact rows."""
    rows: list[dict] = []
    if not ECON_CSV.exists():
        logger.warning("Economic CSV not found: %s", ECON_CSV)
        return rows

    with open(ECON_CSV, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append(row)
    return rows


def extract_storm_name(event_name: str) -> str:
    """Extract storm name from event_name like 'Hurricane Katrina'."""
    for prefix in ("Hurricane ", "Tropical Storm "):
        if event_name.startswith(prefix):
            return event_name[len(prefix):].strip().upper()
    return event_name.strip().upper()


def main() -> None:
    logger.info("Merging hurricane track + economic data...")

    track_data = load_track_data()
    logger.info("  Track records: %d", len(track_data))

    econ_rows = load_econ_data()
    logger.info("  Economic records: %d", len(econ_rows))

    if not econ_rows:
        logger.error("No economic data to merge.")
        return

    # Merge
    merged_rows: list[dict] = []
    for econ_row in econ_rows:
        name = extract_storm_name(econ_row.get("event_name", ""))
        year = int(econ_row.get("data_year", 0))

        track_row = track_data.get((name, year), {})

        merged = {
            "event_name": econ_row.get("event_name", ""),
            "year": year,
            "begin_date": econ_row.get("begin_date", ""),
            "end_date": econ_row.get("end_date", ""),
            "cost_usd_billion_cpi_adjusted": econ_row.get("cost_usd_billion_cpi_adjusted", ""),
            "deaths": econ_row.get("deaths", ""),
            "closest_distance_nm": track_row.get("Closest Distance (NM)", ""),
            "max_wind_kt": track_row.get("Max Wind (kt)", ""),
            "min_pressure_mb": track_row.get("Min Pressure (mb)", ""),
            "storm_id": track_row.get("ID", ""),
        }
        merged_rows.append(merged)

    fieldnames = [
        "event_name", "year", "begin_date", "end_date",
        "cost_usd_billion_cpi_adjusted", "deaths",
        "closest_distance_nm", "max_wind_kt", "min_pressure_mb", "storm_id",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

    logger.info("Wrote %d merged rows to %s", len(merged_rows), OUTPUT_CSV)


if __name__ == "__main__":
    main()
