"""
Shared utilities for all fetch scripts.
Provides download, caching, URL lookup, and logging helpers.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, urlretrieve

# Ensure code/ is on sys.path so sibling imports work
_CODE_DIR = Path(__file__).resolve().parent.parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from config_paths import RAW_DATA_DIR, CONFIG_DIR
from logging_config import setup_logger

logger = setup_logger("fetch.utils")

# ---------------------------------------------------------------------------
# URL registry — maps a keyword tag to a line-match pattern in dataset_sources.txt
# ---------------------------------------------------------------------------
SOURCE_TAGS = {
    "zillow_zhvi_metro": "zhvi/Metro_zhvi",
    "zillow_zhvi_state": "zhvi/State_zhvi",
    "zillow_zhvf_growth": "zhvf_growth/Metro_zhvf",
    "zillow_zori": "zori/Metro_zori",
    "zillow_zorf_growth": "zorf_growth/National_zorf",
    "zillow_inventory": "invt_fs/Metro_invt",
    "zillow_sales_count": "sales_count_now/Metro_sales",
    "zillow_days_on_market": "mean_doz_pending/Metro_mean",
    "zillow_market_temp": "market_temp_index/Metro_market",
    "zillow_new_construction": "new_con_sales_count_raw/Metro_new_con",
    "zillow_income_needed": "new_homeowner_income_needed/Metro_new_homeowner",
    "noaa_hurdat2": "nhc.noaa.gov/data/hurdat2",
    "noaa_economic": "ncei.noaa.gov/access/billions",
}


def read_sources_file() -> list[str]:
    """Read all non-empty, non-comment lines from dataset_sources.txt."""
    sources_file = CONFIG_DIR / "dataset_sources.txt"
    if not sources_file.exists():
        logger.error("dataset_sources.txt not found at %s", sources_file)
        return []
    urls: list[str] = []
    for line in sources_file.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            urls.append(cleaned)
    return urls


def get_url_for_tag(tag: str) -> str | None:
    """
    Look up a URL from dataset_sources.txt by matching the tag pattern.
    Returns the first matching URL or None.
    """
    pattern = SOURCE_TAGS.get(tag)
    if not pattern:
        logger.warning("Unknown source tag: %s", tag)
        return None

    for url in read_sources_file():
        if pattern in url:
            return url

    logger.warning("No URL matched tag '%s' (pattern: '%s')", tag, pattern)
    return None


def filename_from_url(url: str) -> str:
    """Extract a clean filename from a URL, stripping query params."""
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if name:
        return name
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    return f"download_{digest}.bin"


def download_file(url: str, dest_dir: Path | None = None, force: bool = False) -> Path | None:
    """
    Download a file from *url* into *dest_dir* (default: data/raw/).
    Skips download if the file already exists and *force* is False.
    Returns the local Path on success, None on failure.
    """
    dest_dir = dest_dir or RAW_DATA_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = filename_from_url(url)
    dest_path = dest_dir / filename

    if dest_path.exists() and not force:
        logger.info("Already cached: %s", dest_path.name)
        return dest_path

    logger.info("Downloading %s ...", filename)
    try:
        # Check content type first
        with urlopen(url) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" in content_type and not filename.endswith(".html"):
                filename = f"{filename}.html"
                dest_path = dest_dir / filename

        urlretrieve(url, dest_path)
        logger.info("Saved: %s (%d bytes)", dest_path.name, dest_path.stat().st_size)
        return dest_path
    except Exception as exc:
        logger.error("Failed to download %s: %s", url, exc, exc_info=True)
        return None


def fetch_by_tag(tag: str, force: bool = False) -> Path | None:
    """Convenience: resolve tag → URL → download."""
    url = get_url_for_tag(tag)
    if url is None:
        return None
    return download_file(url, force=force)
