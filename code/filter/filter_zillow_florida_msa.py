"""
Filter Zillow CSV files to Florida metropolitan statistical areas only.

Reads: All Zillow CSVs in data/raw/ (Metro_*.csv)
Writes: Individual filtered CSVs to data/processed/ with 'florida_' prefix
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("filter.zillow_florida_msa")

# Columns that are metadata (not date-value columns)
METADATA_COLS = {"RegionID", "SizeRank", "RegionName", "RegionType", "StateName"}


def filter_zillow_csv(input_path: Path, output_path: Path) -> int:
    """
    Filter a Zillow CSV to Florida MSA rows only.
    Returns the number of Florida rows written.
    """
    florida_rows = 0

    with open(input_path, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        if reader.fieldnames is None:
            logger.warning("No headers in %s", input_path.name)
            return 0

        with open(output_path, "w", newline="", encoding="utf-8") as fout:
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                state = row.get("StateName", "")
                region_type = row.get("RegionType", "")
                if state == "FL" and region_type == "msa":
                    writer.writerow(row)
                    florida_rows += 1

    return florida_rows


def main() -> None:
    logger.info("Filtering Zillow CSVs to Florida MSAs...")

    # Find all Metro_*.csv and State_*.csv and National_*.csv in raw
    zillow_csvs = sorted(RAW_DATA_DIR.glob("*_*.csv"))
    if not zillow_csvs:
        logger.warning("No Zillow CSVs found in %s", RAW_DATA_DIR)
        return

    total_files = 0
    total_rows = 0

    for csv_path in zillow_csvs:
        output_name = f"florida_{csv_path.name}"
        output_path = PROCESSED_DATA_DIR / output_name

        logger.info("  Processing %s ...", csv_path.name)
        rows = filter_zillow_csv(csv_path, output_path)
        if rows > 0:
            logger.info("    -> %d Florida MSA rows -> %s", rows, output_name)
            total_files += 1
            total_rows += rows
        else:
            logger.info("    -> No Florida MSA rows (file may be State/National level)")
            # Clean up empty output
            if output_path.exists():
                output_path.unlink()

    logger.info("Done: %d files with %d total Florida rows", total_files, total_rows)


if __name__ == "__main__":
    main()
