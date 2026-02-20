"""
Fetch All Data Sources
=======================
Runs all individual fetch scripts sequentially.
"""
from __future__ import annotations
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logging_config import setup_logger

logger = setup_logger("fetch.all")

FETCH_DIR = Path(__file__).resolve().parent

FETCH_SCRIPTS = [
    "fetch_zillow_zhvi_metro.py",
    "fetch_zillow_zhvi_state.py",
    "fetch_zillow_zhvf_growth.py",
    "fetch_zillow_zori.py",
    "fetch_zillow_zorf_growth.py",
    "fetch_zillow_inventory.py",
    "fetch_zillow_sales_count.py",
    "fetch_zillow_days_on_market.py",
    "fetch_zillow_market_temp.py",
    "fetch_zillow_new_construction.py",
    "fetch_zillow_income_needed.py",
    "fetch_noaa_hurdat2.py",
    "fetch_noaa_economic_impacts.py",
]

def main() -> None:
    logger.info("=" * 60)
    logger.info("FETCH ALL DATA SOURCES")
    logger.info("=" * 60)
    
    results = {"success": [], "failed": []}
    
    for script_name in FETCH_SCRIPTS:
        script_path = FETCH_DIR / script_name
        logger.info("Running %s ...", script_name)
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                results["success"].append(script_name)
                logger.info("  OK: %s", script_name)
            else:
                results["failed"].append(script_name)
                logger.error("  FAILED: %s\n%s", script_name, result.stderr)
        except subprocess.TimeoutExpired:
            results["failed"].append(script_name)
            logger.error("  TIMEOUT: %s", script_name)
        except Exception as exc:
            results["failed"].append(script_name)
            logger.error("  ERROR: %s — %s", script_name, exc)
    
    logger.info("=" * 60)
    logger.info("Fetch complete: %d succeeded, %d failed", len(results["success"]), len(results["failed"]))
    if results["failed"]:
        logger.warning("Failed scripts: %s", ", ".join(results["failed"]))
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
