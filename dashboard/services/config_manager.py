"""
Config Manager — read/write project configuration files.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))
from config_paths import CONFIG_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.config_manager")

SOURCES_FILE = CONFIG_DIR / "dataset_sources.txt"
SOURCES_STATE_FILE = CONFIG_DIR / "dataset_sources_state.json"
COLUMN_CONFIG_FILE = CONFIG_DIR / "column_config.json"

# Auto-labeling patterns for data source URLs
LABEL_PATTERNS = [
    (r"zhvi/Metro_zhvi", "Zillow ZHVI (Metro)", "zillow"),
    (r"zhvi/State_zhvi", "Zillow ZHVI (State)", "zillow"),
    (r"zhvf_growth", "Zillow ZHVF Growth", "zillow"),
    (r"zori/Metro_zori", "Zillow ZORI", "zillow"),
    (r"zorf_growth", "Zillow ZORF Growth", "zillow"),
    (r"invt_fs", "Zillow Inventory", "zillow"),
    (r"sales_count_now", "Zillow Sales Count", "zillow"),
    (r"mean_doz_pending", "Zillow Days on Market", "zillow"),
    (r"market_temp_index", "Zillow Market Temp", "zillow"),
    (r"new_con_sales_count", "Zillow New Construction", "zillow"),
    (r"new_homeowner_income", "Zillow Income Needed", "zillow"),
    (r"nareit\.com", "NAREIT", "nareit"),
    (r"ncei\.noaa\.gov.*billions", "NOAA Economic Impacts", "noaa"),
    (r"oceanservice\.noaa\.gov", "NOAA Historical Hurricanes", "noaa"),
    (r"nhc\.noaa\.gov.*hurdat", "NOAA HURDAT2", "noaa"),
]


def _auto_label(url: str) -> tuple[str, str]:
    """Return (label, type_badge) for a URL."""
    for pattern, label, badge in LABEL_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return label, badge
    return "Unknown Source", "other"


# ── source enabled/disabled state ────────────────────────────────

def _load_source_state() -> dict:
    """Load disabled-source state from JSON."""
    if SOURCES_STATE_FILE.exists():
        try:
            return json.loads(SOURCES_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_source_state(state: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SOURCES_STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)


def get_disabled_urls() -> set[str]:
    """Return the set of URLs currently marked as disabled."""
    state = _load_source_state()
    return set(state.get("disabled_urls", []))


def set_source_enabled(url: str, enabled: bool) -> None:
    """Enable or disable a single data source by URL."""
    state = _load_source_state()
    disabled = set(state.get("disabled_urls", []))
    if enabled:
        disabled.discard(url)
    else:
        disabled.add(url)
    state["disabled_urls"] = sorted(disabled)
    _save_source_state(state)
    logger.info("Source %s: %s", "enabled" if enabled else "disabled", url[:80])


def get_sources() -> list[dict]:
    """Read data sources and return annotated list (with enabled flag)."""
    if not SOURCES_FILE.exists():
        return []
    disabled = get_disabled_urls()
    urls = []
    for line in SOURCES_FILE.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        label, badge = _auto_label(cleaned)
        urls.append({
            "url": cleaned,
            "label": label,
            "type": badge,
            "enabled": cleaned not in disabled,
        })
    return urls


def save_sources(urls: list[str]) -> None:
    """Write URLs back to dataset_sources.txt."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    content = "\n".join(u.strip() for u in urls if u.strip()) + "\n"
    SOURCES_FILE.write_text(content, encoding="utf-8")
    logger.info("Saved %d sources to %s", len(urls), SOURCES_FILE)


def get_column_config() -> dict:
    """Read column configuration."""
    if COLUMN_CONFIG_FILE.exists():
        return json.loads(COLUMN_CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def save_column_config(config: dict) -> None:
    """Write column configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(COLUMN_CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)
    logger.info("Saved column config to %s", COLUMN_CONFIG_FILE)
