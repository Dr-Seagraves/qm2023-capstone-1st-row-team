"""
Filter All — runs all filter scripts sequentially.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logging_config import setup_logger

logger = setup_logger("filter.all")

FILTER_DIR = Path(__file__).resolve().parent

FILTER_SCRIPTS = [
    "filter_florida_storms_60nm.py",
    "filter_florida_landfall_hurricanes.py",
    "filter_zillow_florida_msa.py",
]


def main() -> None:
    logger.info("=" * 60)
    logger.info("FILTER ALL DATA")
    logger.info("=" * 60)

    results = {"success": [], "failed": []}

    for script_name in FILTER_SCRIPTS:
        script_path = FILTER_DIR / script_name
        logger.info("Running %s ...", script_name)
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True, text=True, timeout=300,
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

    logger.info("Filter complete: %d succeeded, %d failed",
                len(results["success"]), len(results["failed"]))


if __name__ == "__main__":
    main()
