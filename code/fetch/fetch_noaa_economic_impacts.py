"""
Fetch NOAA Billion-Dollar Weather/Climate Disaster data.
Downloads to data/raw/.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fetch._fetch_utils import fetch_by_tag, logger

TAG = "noaa_economic"

def main() -> None:
    logger.info("Fetching NOAA economic impact data...")
    result = fetch_by_tag(TAG)
    if result:
        logger.info("Success: %s", result)
    else:
        logger.error("Failed to fetch NOAA economic data")
        sys.exit(1)

if __name__ == "__main__":
    main()
