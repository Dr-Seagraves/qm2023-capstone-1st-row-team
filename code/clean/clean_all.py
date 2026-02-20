"""
Clean All — runs all clean scripts sequentially.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logging_config import setup_logger

logger = setup_logger("clean.all")

CLEAN_DIR = Path(__file__).resolve().parent

CLEAN_SCRIPTS = [
    "clean_zillow.py",
    "clean_hurdat2.py",
    "clean_economic.py",
]


def main() -> None:
    logger.info("=" * 60)
    logger.info("CLEAN ALL DATA")
    logger.info("=" * 60)

    results = {"success": [], "failed": []}

    for script_name in CLEAN_SCRIPTS:
        script_path = CLEAN_DIR / script_name
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

    logger.info("Clean complete: %d succeeded, %d failed",
                len(results["success"]), len(results["failed"]))


if __name__ == "__main__":
    main()
