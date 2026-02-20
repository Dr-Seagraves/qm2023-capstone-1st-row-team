"""
Data Scanner — wraps code/generate_data_dictionary.py for dashboard use.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))
from config_paths import FINAL_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.data_scanner")


def scan_and_generate() -> dict:
    """Run the data dictionary generator and return results."""
    from generate_data_dictionary import main as gen_main
    return gen_main()


def get_cached_dictionary() -> dict:
    """Return the cached data dictionary or empty structure."""
    dict_path = FINAL_DATA_DIR / "data_dictionary.json"
    if dict_path.exists():
        return json.loads(dict_path.read_text(encoding="utf-8"))
    return {"version": "1.0", "datasets": {}}
