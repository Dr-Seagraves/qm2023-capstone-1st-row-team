"""
Merge multiple Zillow metrics into a single consolidated CSV.

Reads: Filtered Florida Zillow CSVs in data/processed/ (florida_Metro_*.csv)
Writes: data/processed/florida_zillow_metrics_monthly.csv

Each Zillow CSV has the same structure: metadata columns + monthly date columns.
This script pivots them into long format: Metro | Date | Metric1 | Metric2 | ...
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("merge.zillow_metrics")

METADATA_COLS = {"RegionID", "SizeRank", "RegionName", "RegionType", "StateName"}

# Map raw filenames to metric labels
METRIC_MAP = {
    "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "ZHVI",
    "State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "ZHVI_State",
    "Metro_zhvf_growth_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "ZHVF_Growth",
    "Metro_zori_uc_sfrcondomfr_sm_month.csv": "ZORI",
    "National_zorf_growth_uc_sfr_sm_month.csv": "ZORF_Growth",
    "Metro_invt_fs_uc_sfrcondo_sm_month.csv": "Inventory",
    "Metro_sales_count_now_uc_sfrcondo_month.csv": "Sales_Count",
    "Metro_mean_doz_pending_uc_sfrcondo_sm_month.csv": "Days_on_Market",
    "Metro_market_temp_index_uc_sfrcondo_month.csv": "Market_Temp",
    "Metro_new_con_sales_count_raw_uc_sfrcondo_month.csv": "New_Construction",
    "Metro_new_homeowner_income_needed_downpayment_0.20_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "Income_Needed",
}

OUTPUT_CSV = PROCESSED_DATA_DIR / "florida_zillow_metrics_monthly.csv"


def process_zillow_file(csv_path: Path, metric_name: str) -> dict[str, dict[str, float]]:
    """
    Read a Zillow CSV (already Florida-filtered or raw) and extract
    {metro_name: {date_str: value}} for Florida MSAs.
    """
    data: dict[str, dict[str, float]] = {}

    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return data

        date_cols = [c for c in reader.fieldnames if c not in METADATA_COLS]

        for row in reader:
            state = row.get("StateName", "")
            region_type = row.get("RegionType", "")
            if state != "FL" or region_type != "msa":
                continue

            metro = row.get("RegionName", "")
            if not metro:
                continue

            if metro not in data:
                data[metro] = {}

            for date_col in date_cols:
                try:
                    data[metro][date_col] = float(row[date_col])
                except (ValueError, KeyError):
                    pass

    return data


def main() -> None:
    logger.info("Merging Zillow metrics for Florida MSAs...")

    # Collect all data: {metro: {date: {metric: value}}}
    all_data: dict[str, dict[str, dict[str, float]]] = {}
    all_dates: set[str] = set()
    all_metrics: set[str] = set()

    for filename, metric_name in METRIC_MAP.items():
        csv_path = RAW_DATA_DIR / filename
        if not csv_path.exists():
            logger.warning("  Missing: %s — skipping %s", filename, metric_name)
            continue

        logger.info("  Reading %s as '%s'...", filename, metric_name)
        metro_data = process_zillow_file(csv_path, metric_name)

        for metro, date_values in metro_data.items():
            if metro not in all_data:
                all_data[metro] = {}
            for date_str, value in date_values.items():
                if date_str not in all_data[metro]:
                    all_data[metro][date_str] = {}
                all_data[metro][date_str][metric_name] = value
                all_dates.add(date_str)

        all_metrics.add(metric_name)
        logger.info("    -> %d metros", len(metro_data))

    if not all_data:
        logger.error("No data collected. Ensure Zillow CSVs exist in %s", RAW_DATA_DIR)
        sys.exit(1)

    sorted_metrics = sorted(all_metrics)
    sorted_dates = sorted(all_dates)

    # Write consolidated output
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Metro", "Date"] + sorted_metrics)

        row_count = 0
        for metro in sorted(all_data.keys()):
            for date_str in sorted_dates:
                metric_values = all_data[metro].get(date_str, {})
                row = [metro, date_str] + [
                    metric_values.get(m, "") for m in sorted_metrics
                ]
                writer.writerow(row)
                row_count += 1

    logger.info(
        "Wrote %s: %d metros, %d metrics, %d rows",
        OUTPUT_CSV.name, len(all_data), len(all_metrics), row_count,
    )


if __name__ == "__main__":
    main()
