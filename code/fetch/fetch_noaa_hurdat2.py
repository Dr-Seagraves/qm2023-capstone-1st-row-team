"""
Fetch HURDAT2 hurricane track data from NOAA NHC.
Downloads to data/raw/hurdat2_raw.txt.
"""
from __future__ import annotations
import sys
from pathlib import Path
from urllib.request import urlretrieve

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config_paths import RAW_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("fetch.noaa_hurdat2")

HURDAT2_URL = "https://www.nhc.noaa.gov/data/hurdat2/hurdat2.txt"
OUTPUT_FILE = RAW_DATA_DIR / "hurdat2_raw.txt"

def main(force: bool = False) -> Path | None:
    if OUTPUT_FILE.exists() and not force:
        logger.info("HURDAT2 data already cached at %s", OUTPUT_FILE)
        return OUTPUT_FILE
    
    logger.info("Downloading HURDAT2 from %s ...", HURDAT2_URL)
    try:
        urlretrieve(HURDAT2_URL, OUTPUT_FILE)
        logger.info("Saved HURDAT2 data: %s (%d bytes)", OUTPUT_FILE.name, OUTPUT_FILE.stat().st_size)
        return OUTPUT_FILE
    except Exception as exc:
        logger.error("Failed to download HURDAT2: %s", exc, exc_info=True)
        return None

if __name__ == "__main__":
    result = main()
    if not result:
        sys.exit(1)
