"""
Filter HURDAT2 storms to those within 60 NM of Florida (2004-2025).

Reads: data/raw/hurdat2_raw.txt (downloaded by fetch/fetch_noaa_hurdat2.py)
Writes: data/processed/florida_storms_60nm_2004_2025.csv
        data/processed/florida_storms_60nm_summary.csv
"""

from __future__ import annotations

import csv
import sys
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("filter.florida_storms_60nm")

INPUT_FILE = RAW_DATA_DIR / "hurdat2_raw.txt"
OUTPUT_DETAIL = PROCESSED_DATA_DIR / "florida_storms_60nm_2004_2025.csv"
OUTPUT_SUMMARY = PROCESSED_DATA_DIR / "florida_storms_60nm_summary.csv"

FLORIDA_LAT = 27.5
FLORIDA_LON = -82.0
MAX_DISTANCE_NM = 60
YEAR_MIN = 2004
YEAR_MAX = 2025


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in nautical miles."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * asin(sqrt(a)) * 3440.065


def parse_hurdat2(file_path: Path) -> list[dict]:
    """Parse HURDAT2 text into a list of record dicts."""
    records: list[dict] = []
    with open(file_path, "r", encoding="utf-8") as fh:
        current_storm: dict | None = None
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line[0].isalpha():
                parts = line.split(",")
                if len(parts) >= 3:
                    current_storm = {
                        "id": parts[0].strip(),
                        "name": parts[1].strip(),
                    }
            elif current_storm:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 8:
                    continue
                try:
                    lat_str = parts[4]
                    lon_str = parts[5]
                    lat = float(lat_str[:-1]) * (1 if lat_str[-1] == "N" else -1)
                    lon = float(lon_str[:-1]) * (1 if lon_str[-1] == "E" else -1)
                    max_wind = int(parts[6]) if parts[6].strip().isdigit() else None
                    min_pressure = int(parts[7]) if parts[7].strip().isdigit() else None
                    date_str = parts[0]
                    year = int(date_str[:4])
                    records.append(
                        {
                            "storm_id": current_storm["id"],
                            "storm_name": current_storm["name"],
                            "date": date_str,
                            "time": parts[1],
                            "status": parts[3],
                            "lat": lat,
                            "lon": lon,
                            "max_wind": max_wind,
                            "min_pressure": min_pressure,
                            "year": year,
                        }
                    )
                except (ValueError, IndexError):
                    continue
    return records


def filter_and_save() -> None:
    if not INPUT_FILE.exists():
        logger.error("Input file not found: %s. Run fetch_noaa_hurdat2.py first.", INPUT_FILE)
        sys.exit(1)

    logger.info("Parsing HURDAT2 data from %s ...", INPUT_FILE)
    records = parse_hurdat2(INPUT_FILE)
    logger.info("Total HURDAT2 records: %d", len(records))

    # Compute distance and filter
    filtered: list[dict] = []
    for rec in records:
        dist = haversine_distance(FLORIDA_LAT, FLORIDA_LON, rec["lat"], rec["lon"])
        rec["distance_nm"] = round(dist, 1)
        if dist <= MAX_DISTANCE_NM and YEAR_MIN <= rec["year"] <= YEAR_MAX:
            filtered.append(rec)

    # Identify unique storms
    storm_ids = {r["storm_id"] for r in filtered}

    # Keep all records for those storms within the year range
    final_records = [
        r for r in records
        if r["storm_id"] in storm_ids and YEAR_MIN <= r["year"] <= YEAR_MAX
    ]
    for r in final_records:
        if "distance_nm" not in r:
            r["distance_nm"] = round(
                haversine_distance(FLORIDA_LAT, FLORIDA_LON, r["lat"], r["lon"]), 1
            )

    logger.info(
        "Storms within %d NM of Florida (%d-%d): %d storms, %d records",
        MAX_DISTANCE_NM, YEAR_MIN, YEAR_MAX, len(storm_ids), len(final_records),
    )

    # Write detail CSV
    detail_fields = [
        "storm_id", "storm_name", "date", "time", "status",
        "lat", "lon", "max_wind", "min_pressure", "year", "distance_nm",
    ]
    with open(OUTPUT_DETAIL, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=detail_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(final_records)
    logger.info("Wrote detail CSV: %s (%d rows)", OUTPUT_DETAIL, len(final_records))

    # Build and write summary
    summary_rows: list[dict] = []
    for sid in sorted(storm_ids):
        storm_records = [r for r in final_records if r["storm_id"] == sid]
        name = storm_records[0]["storm_name"]
        year = storm_records[0]["year"]
        closest = min(r["distance_nm"] for r in storm_records)
        max_wind = max((r["max_wind"] for r in storm_records if r["max_wind"]), default=None)
        min_pres = min((r["min_pressure"] for r in storm_records if r["min_pressure"]), default=None)
        summary_rows.append({
            "Year": year,
            "Storm": name,
            "ID": sid,
            "Closest Distance (NM)": closest,
            "Max Wind (kt)": max_wind,
            "Min Pressure (mb)": min_pres,
        })
    summary_rows.sort(key=lambda r: r["Year"])

    summary_fields = ["Year", "Storm", "ID", "Closest Distance (NM)", "Max Wind (kt)", "Min Pressure (mb)"]
    with open(OUTPUT_SUMMARY, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)
    logger.info("Wrote summary CSV: %s (%d storms)", OUTPUT_SUMMARY, len(summary_rows))


def main() -> None:
    filter_and_save()


if __name__ == "__main__":
    main()
