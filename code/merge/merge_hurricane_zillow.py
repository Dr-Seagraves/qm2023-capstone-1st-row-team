"""
Merge hurricane event data with Zillow housing metrics (stub).

This is the final analysis merge: hurricane events x Zillow time-series.
To be implemented once the team finalizes the analysis methodology.

Reads:
  data/processed/florida_hurricane_economic_merged.csv
  data/processed/florida_zillow_metrics_monthly.csv
Writes:
  data/final/hurricane_zillow_panel.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import PROCESSED_DATA_DIR, FINAL_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("merge.hurricane_zillow")

HURRICANE_CSV = PROCESSED_DATA_DIR / "florida_hurricane_economic_merged.csv"
ZILLOW_CSV = PROCESSED_DATA_DIR / "florida_zillow_metrics_monthly.csv"
OUTPUT_CSV = FINAL_DATA_DIR / "hurricane_zillow_panel.csv"


def main() -> None:
    logger.info("Merge Hurricane + Zillow data (stub)")

    if not HURRICANE_CSV.exists():
        logger.warning("Hurricane merged CSV not found: %s", HURRICANE_CSV)
    if not ZILLOW_CSV.exists():
        logger.warning("Zillow metrics CSV not found: %s", ZILLOW_CSV)

    # -------------------------------------------------------------------------
    # TODO: Implement the merge logic.
    #
    # Suggested approach:
    # 1. Load hurricane events with dates and severity metrics
    # 2. Load Zillow monthly panel (Metro x Date x Metrics)
    # 3. For each hurricane, identify affected MSAs and time windows
    #    (e.g., 6 months before / 12 months after)
    # 4. Create panel columns: pre_event, post_event, event_severity, etc.
    # 5. Output a ready-for-regression panel dataset
    # -------------------------------------------------------------------------

    logger.info(
        "This script is a stub. Implement the merge logic to produce %s",
        OUTPUT_CSV,
    )


if __name__ == "__main__":
    main()
