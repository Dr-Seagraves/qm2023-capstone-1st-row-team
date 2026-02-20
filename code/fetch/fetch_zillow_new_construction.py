"""
Fetch Zillow New Construction Sales from Zillow Research.
Downloads to data/raw/.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fetch._fetch_utils import fetch_by_tag, logger

TAG = "zillow_new_construction"

def main() -> None:
    logger.info("Fetching Zillow New Construction Sales...")
    result = fetch_by_tag(TAG)
    if result:
        logger.info("Success: %s", result)
    else:
        logger.error("Failed to fetch Zillow New Construction Sales")
        sys.exit(1)

if __name__ == "__main__":
    main()
