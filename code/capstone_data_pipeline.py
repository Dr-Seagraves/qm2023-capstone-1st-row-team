"""
QM 2023 Capstone Project: Milestone 1 Data Pipeline
Team: 1st Row Team
Members: Nevaeh Marquez, Logan Ledbetter, Raleigh Elizabeth Wullkotte, Sam Bronner
Date: 2026-02-20
Dataset: Housing — Florida Hurricane Exposure & Housing Market

This script fetches, cleans, and merges Florida hurricane track data,
NOAA billion-dollar disaster economic impact data, and Zillow housing
market indicators into a tidy panel structure (Metro × Month) for
Florida MSAs.
"""

# =============================================================================
# Section 1: Imports and setup
# =============================================================================

import csv
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import urlretrieve, Request, urlopen

import numpy as np
import pandas as pd

# -- Paths (all relative to the project root, one level above code/) --
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FINAL_DATA_DIR = PROJECT_ROOT / "data" / "final"

for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FINAL_DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -- Source URLs --
# Zillow housing indicator CSVs (all national metro-level files)
ZILLOW_URLS = {
    "ZHVI": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "ZHVF_Growth": "https://files.zillowstatic.com/research/public_csvs/zhvf_growth/Metro_zhvf_growth_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "ZORI": "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv",
    "Inventory": "https://files.zillowstatic.com/research/public_csvs/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv",
    "Sales_Count": "https://files.zillowstatic.com/research/public_csvs/sales_count_now/Metro_sales_count_now_uc_sfrcondo_month.csv",
    "Days_on_Market": "https://files.zillowstatic.com/research/public_csvs/mean_doz_pending/Metro_mean_doz_pending_uc_sfrcondo_sm_month.csv",
    "Market_Temp": "https://files.zillowstatic.com/research/public_csvs/market_temp_index/Metro_market_temp_index_uc_sfrcondo_month.csv",
    "Income_Needed": "https://files.zillowstatic.com/research/public_csvs/new_homeowner_income_needed/Metro_new_homeowner_income_needed_downpayment_0.20_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
}

# NOAA HURDAT2 Atlantic hurricane track data (fixed-width text)
# The filename changes with each data release, so we auto-detect the latest.
HURDAT2_DIR_URL = "https://www.nhc.noaa.gov/data/hurdat/"
HURDAT2_FALLBACK = "hurdat2-1851-2024-040425.txt"  # Apr 4, 2025 release

# NOAA Billion-Dollar Disasters API — tropical cyclone events, CPI-adjusted
NOAA_ECON_URL = "https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.json?disasters[]=tropical-cyclone"

# Zillow metadata columns (not date values)
ZILLOW_META_COLS = {"RegionID", "SizeRank", "RegionName", "RegionType", "StateName"}


def resolve_hurdat2_url():
    """Auto-detect the latest HURDAT2 Atlantic file from the NHC directory."""
    try:
        html = urlopen(HURDAT2_DIR_URL).read().decode()
        files = re.findall(r'href="(hurdat2-1851-[^"]+\.txt)"', html)
        if files:
            latest = sorted(files)[-1]
            print(f"  Auto-detected HURDAT2 file: {latest}")
            return HURDAT2_DIR_URL + latest
    except Exception as e:
        print(f"  WARNING: Could not auto-detect HURDAT2 file ({e}), using fallback.")
    return HURDAT2_DIR_URL + HURDAT2_FALLBACK


def download_file(url, dest_path, force=False):
    """Download a file from url to dest_path. Skip if already cached."""
    if dest_path.exists() and not force:
        print(f"  [cached] {dest_path.name}")
        return True
    print(f"  Downloading {dest_path.name} ...")
    try:
        urlretrieve(url, str(dest_path))
        return True
    except Exception as e:
        print(f"  ERROR downloading {url}: {e}")
        return False


def haversine_nm(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in nautical miles."""
    R_NM = 3440.065  # Earth radius in nautical miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R_NM * math.asin(math.sqrt(a))


def parse_hurdat2(text):
    """
    Parse HURDAT2 fixed-width text into a list of dicts.
    Returns list of track-point records with storm metadata.

    HURDAT2 format:
      - Header line: AL092004, FRANCES, 34,  (storm ID, name, # entries)
      - Data line: 20040825, 1800, , TD, 13.7N, 42.2W, 30, 1009, ...
    """
    records = []
    current_id = None
    current_name = None

    for line in text.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if not parts:
            continue

        # Header line: starts with AL/EP/CP, has storm ID + name
        if parts[0].startswith(("AL", "EP", "CP")) and len(parts) >= 3:
            current_id = parts[0]
            current_name = parts[1].strip()
            continue

        # Data line: date (8 chars), time (4 chars), record_id, status, lat, lon, wind, pressure, ...
        if len(parts) >= 8 and len(parts[0]) == 8 and parts[0].isdigit():
            date_str = parts[0]      # YYYYMMDD
            time_str = parts[1]      # HHMM
            record_id = parts[2]     # blank, L (landfall), W, S, etc.
            status = parts[3]        # HU, TS, TD, EX, etc.

            # Parse lat/lon: "28.0N" -> 28.0, "80.1W" -> -80.1
            lat_str = parts[4]
            lon_str = parts[5]
            try:
                lat = float(lat_str[:-1]) * (1 if lat_str[-1] == "N" else -1)
                lon = float(lon_str[:-1]) * (-1 if lon_str[-1] == "W" else 1)
            except (ValueError, IndexError):
                continue

            # Wind and pressure
            try:
                max_wind = int(parts[6]) if parts[6] not in ("", "-999", "-99") else None
            except ValueError:
                max_wind = None
            try:
                min_pressure = int(parts[7]) if parts[7] not in ("", "-999", "-99") else None
            except ValueError:
                min_pressure = None

            records.append({
                "storm_id": current_id,
                "storm_name": current_name,
                "date": date_str,
                "time": time_str,
                "record_id": record_id,
                "status": status,
                "lat": lat,
                "lon": lon,
                "max_wind": max_wind,
                "min_pressure": min_pressure,
            })

    return records


# Florida geographic center for proximity filtering
FL_CENTER_LAT = 27.5
FL_CENTER_LON = -82.0
FL_PROXIMITY_NM = 60  # nautical miles threshold


# =============================================================================
# Section 2: Load primary dataset (Zillow housing data)
# =============================================================================

print("=" * 70)
print("SECTION 2: Load Primary Dataset — Zillow Housing Indicators")
print("=" * 70)

# 2a. Download all Zillow CSVs to data/raw/ (skip if cached)
print("\nDownloading Zillow CSVs...")
for metric_name, url in ZILLOW_URLS.items():
    filename = url.split("/")[-1]
    download_file(url, RAW_DATA_DIR / filename)

# 2b. Load each Zillow Metro CSV, filter to Florida MSAs, pivot to long format
# The Zillow files are wide-format: metadata cols + one column per YYYY-MM-DD date
print("\nLoading and filtering Zillow data to Florida MSAs...")

zillow_long_frames = []
zillow_initial_rows = 0
zillow_florida_rows = 0

# Map filenames to metric labels
ZILLOW_FILE_METRIC = {
    "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "ZHVI",
    "Metro_zhvf_growth_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "ZHVF_Growth",
    "Metro_zori_uc_sfrcondomfr_sm_month.csv": "ZORI",
    "Metro_invt_fs_uc_sfrcondo_sm_month.csv": "Inventory",
    "Metro_sales_count_now_uc_sfrcondo_month.csv": "Sales_Count",
    "Metro_mean_doz_pending_uc_sfrcondo_sm_month.csv": "Days_on_Market",
    "Metro_market_temp_index_uc_sfrcondo_month.csv": "Market_Temp",
    "Metro_new_homeowner_income_needed_downpayment_0.20_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv": "Income_Needed",
}

# Collect all metrics into one wide dict: {metro: {date: {metric: value}}}
metro_data = {}   # metro_name -> {date_str -> {metric_name -> value}}
all_dates = set()
loaded_metrics = []

for filename, metric_name in ZILLOW_FILE_METRIC.items():
    csv_path = RAW_DATA_DIR / filename
    if not csv_path.exists():
        print(f"  WARNING: Missing {filename} — skipping {metric_name}")
        continue

    # Read with csv.DictReader for efficiency (these files can be large)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            continue

        date_cols = [c for c in reader.fieldnames if c not in ZILLOW_META_COLS]
        file_total = 0
        file_florida = 0

        for row in reader:
            file_total += 1
            # Filter to Florida MSAs only
            if row.get("StateName") != "FL" or row.get("RegionType") != "msa":
                continue

            file_florida += 1
            metro = row.get("RegionName", "")
            if not metro:
                continue

            if metro not in metro_data:
                metro_data[metro] = {}

            for date_col in date_cols:
                val = row.get(date_col, "")
                if val == "":
                    continue
                try:
                    val_float = float(val)
                except ValueError:
                    continue

                if date_col not in metro_data[metro]:
                    metro_data[metro][date_col] = {}
                metro_data[metro][date_col][metric_name] = val_float
                all_dates.add(date_col)

        zillow_initial_rows += file_total
        zillow_florida_rows += file_florida
        loaded_metrics.append(metric_name)
        print(f"  {metric_name}: {file_total} total rows, {file_florida} Florida MSA rows")

# Build a strict long-format DataFrame: Metro | Date | metric | value
sorted_dates = sorted(all_dates)
sorted_metrics = sorted(loaded_metrics)

panel_rows = []
for metro in sorted(metro_data.keys()):
    for date_str in sorted_dates:
        metrics = metro_data[metro].get(date_str, {})
        # Only include rows where at least one metric has a value
        if metrics:
            for m in sorted_metrics:
                if m in metrics:
                    panel_rows.append({
                        "Metro": metro,
                        "Date": date_str,
                        "metric": m,
                        "value": metrics[m],
                    })

zillow_panel = pd.DataFrame(panel_rows)

print(f"\nZillow primary dataset loaded:")
print(f"  Total rows across all files: {zillow_initial_rows}")
print(f"  Florida MSA rows: {zillow_florida_rows}")
print(f"  Long rows (Metro × Date × metric): {zillow_panel.shape}")
print(f"  Unique metros: {zillow_panel['Metro'].nunique()}")
print(f"  Date range: {zillow_panel['Date'].min()} to {zillow_panel['Date'].max()}")
print(f"  Metrics loaded: {sorted_metrics}")
print(f"\nFirst 5 rows:")
print(zillow_panel.head().to_string())
print(f"\nColumn info:")
print(zillow_panel.dtypes.to_string())


# =============================================================================
# Section 3: Clean data (missing values, outliers, duplicates)
# =============================================================================

print("\n" + "=" * 70)
print("SECTION 3: Clean Data — Missing Values, Outliers, Duplicates")
print("=" * 70)

# 3a. Document missing values BEFORE cleaning
print("\n--- Missing values before cleaning ---")
missing_before = zillow_panel.isnull().sum()
missing_pct_before = 100 * zillow_panel.isnull().mean()
for col in zillow_panel.columns:
    if missing_before[col] > 0:
        print(f"  {col}: {missing_before[col]} missing ({missing_pct_before[col]:.1f}%)")

n_before_clean = len(zillow_panel)
print(f"\nTotal rows before cleaning: {n_before_clean}")

# 3b. Standardize column names — already clean from construction, but ensure lowercase
zillow_panel.columns = [c.strip() for c in zillow_panel.columns]

# 3c. Parse Date column to datetime, then to consistent YYYY-MM-DD string
zillow_panel["Date"] = pd.to_datetime(zillow_panel["Date"], errors="coerce")
date_nulls = zillow_panel["Date"].isnull().sum()
if date_nulls > 0:
    print(f"  Dropping {date_nulls} rows with unparseable dates")
    zillow_panel = zillow_panel.dropna(subset=["Date"])

# 3d. Drop rows with missing value in long schema
n_null_value = zillow_panel["value"].isnull().sum()
if n_null_value > 0:
    print(f"  Dropping {n_null_value} rows with null value")
    zillow_panel = zillow_panel.dropna(subset=["value"])

# 3e. Handle duplicates: one row per Metro × Date × metric
n_dupes = zillow_panel.duplicated(subset=["Metro", "Date", "metric"], keep="first").sum()
if n_dupes > 0:
    print(f"  Dropping {n_dupes} duplicate Metro×Date×metric rows (keeping first)")
    zillow_panel = zillow_panel.drop_duplicates(subset=["Metro", "Date", "metric"], keep="first")

# 3f. Outlier treatment — winsorize continuous metrics at 1st/99th percentile
#     This caps extreme values while preserving trends. Appropriate for housing
#     market data where extreme outliers may reflect data errors or edge cases.
print("\n--- Outlier treatment (winsorize 1st/99th percentile) ---")
for metric_name, idx in zillow_panel.groupby("metric").groups.items():
    series = zillow_panel.loc[idx, "value"].dropna()
    if len(series) < 10:
        continue
    p01 = series.quantile(0.01)
    p99 = series.quantile(0.99)
    n_clipped = ((series < p01) | (series > p99)).sum()
    if n_clipped > 0:
        zillow_panel.loc[idx, "value"] = zillow_panel.loc[idx, "value"].clip(lower=p01, upper=p99)
        print(f"  {metric_name}: clipped {n_clipped} values to [{p01:.2f}, {p99:.2f}]")

# 3g. Document AFTER cleaning
n_after_clean = len(zillow_panel)
print(f"\n--- After cleaning ---")
print(f"  Rows: {n_before_clean} → {n_after_clean} (dropped {n_before_clean - n_after_clean})")
missing_after = zillow_panel.isnull().sum()
missing_pct_after = 100 * zillow_panel.isnull().mean()
for col in zillow_panel.columns:
    if missing_after[col] > 0:
        print(f"  {col}: {missing_after[col]} missing ({missing_pct_after[col]:.1f}%)")


# =============================================================================
# Section 4: Fetch/load supplementary data (hurricane + economic indicators)
# =============================================================================

print("\n" + "=" * 70)
print("SECTION 4: Fetch Supplementary Data — Hurricanes & Economic Impacts")
print("=" * 70)

# 4a. Fetch and parse HURDAT2 hurricane track data
print("\n--- Fetching HURDAT2 hurricane track data ---")
hurdat2_url = resolve_hurdat2_url()
hurdat2_path = RAW_DATA_DIR / "hurdat2_raw.txt"
download_file(hurdat2_url, hurdat2_path)

print("  Parsing HURDAT2 fixed-width format...")
with open(hurdat2_path, "r", encoding="utf-8") as f:
    hurdat2_text = f.read()
track_records = parse_hurdat2(hurdat2_text)
print(f"  Total track points parsed: {len(track_records)}")

# 4b. Filter to storms within 60 NM of Florida center, years 2000–2025
#     We use a broader time range than just landfall events to capture storms
#     that may have influenced market expectations even without direct landfall.
print(f"\n--- Filtering storms within {FL_PROXIMITY_NM} NM of Florida ({FL_CENTER_LAT}°N, {abs(FL_CENTER_LON)}°W) ---")
print(f"    Year range: 2000–2025")

florida_storm_ids = set()
storm_min_dist = {}  # storm_id -> minimum distance to Florida center (NM)

for rec in track_records:
    year = int(rec["date"][:4])
    if year < 2000 or year > 2025:
        continue

    dist = haversine_nm(FL_CENTER_LAT, FL_CENTER_LON, rec["lat"], rec["lon"])
    sid = rec["storm_id"]

    if sid not in storm_min_dist or dist < storm_min_dist[sid]:
        storm_min_dist[sid] = dist

    if dist <= FL_PROXIMITY_NM:
        florida_storm_ids.add(sid)

# Collect summary for Florida-proximity storms
florida_storms = []
for sid in florida_storm_ids:
    storm_points = [r for r in track_records if r["storm_id"] == sid]
    if not storm_points:
        continue

    name = storm_points[0]["storm_name"]
    year = int(storm_points[0]["date"][:4])
    winds = [r["max_wind"] for r in storm_points if r["max_wind"] is not None]
    pressures = [r["min_pressure"] for r in storm_points if r["min_pressure"] is not None]
    has_landfall = any(r["record_id"] == "L" for r in storm_points)

    florida_storms.append({
        "storm_id": sid,
        "storm_name": name,
        "year": year,
        "closest_distance_nm": round(storm_min_dist[sid], 1),
        "max_wind_kt": max(winds) if winds else None,
        "min_pressure_mb": min(pressures) if pressures else None,
        "has_florida_landfall": has_landfall,
    })

florida_storms_df = pd.DataFrame(florida_storms).sort_values(["year", "storm_name"]).reset_index(drop=True)
print(f"  Florida-proximity storms found: {len(florida_storms_df)}")
if not florida_storms_df.empty:
    print(f"  Year range: {florida_storms_df['year'].min()} to {florida_storms_df['year'].max()}")
    print(f"\n  Storm summary:")
    print(florida_storms_df.to_string(index=False))

# Save filtered storm data to processed/ in long format
storm_id_cols = ["storm_id", "storm_name", "year"]
storm_value_cols = [c for c in florida_storms_df.columns if c not in storm_id_cols]
florida_storms_long = florida_storms_df.melt(
    id_vars=storm_id_cols,
    value_vars=storm_value_cols,
    var_name="metric",
    value_name="value",
)
storms_long_path = PROCESSED_DATA_DIR / "florida_storms_60nm_2000_2025_long.csv"
storms_legacy_path = PROCESSED_DATA_DIR / "florida_storms_60nm_2000_2025.csv"
florida_storms_long.to_csv(storms_long_path, index=False)
# Keep legacy filename for backward compatibility; file content is long-format.
florida_storms_long.to_csv(storms_legacy_path, index=False)
print(f"\n  Saved: data/processed/florida_storms_60nm_2000_2025_long.csv")
print(f"  Saved: data/processed/florida_storms_60nm_2000_2025.csv (legacy long-format alias)")

# 4c. Fetch NOAA economic impact data (tropical cyclone events)
print("\n--- Fetching NOAA Billion-Dollar Disaster economic data (tropical cyclones) ---")
noaa_econ_path = RAW_DATA_DIR / "noaa_tropical_cyclone_events.json"

if not noaa_econ_path.exists():
    print(f"  Downloading from NOAA API...")
    try:
        req = Request(NOAA_ECON_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        with open(noaa_econ_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved: {noaa_econ_path.name}")
    except Exception as e:
        print(f"  ERROR fetching NOAA economic data: {e}")
        data = {"data": []}
else:
    print(f"  [cached] {noaa_econ_path.name}")
    with open(noaa_econ_path, "r", encoding="utf-8") as f:
        data = json.load(f)

# Parse economic events
econ_events = []
for event in data.get("data", []):
    name = event.get("name", "")
    # Extract storm name: "Hurricane Frances (September 2004)" -> "FRANCES"
    clean_name = name
    for prefix in ["Hurricane ", "Tropical Storm ", "Tropical Cyclone "]:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break
    # Remove parenthetical date info
    if "(" in clean_name:
        clean_name = clean_name[:clean_name.index("(")].strip()
    clean_name = clean_name.upper()

    # Parse dates: YYYYMMDD integer format
    beg = str(event.get("begDate", ""))
    end = str(event.get("endDate", ""))
    try:
        year = int(beg[:4]) if len(beg) >= 4 else None
    except ValueError:
        year = None

    # Cost: API returns millions; convert to billions
    cost_millions = event.get("adjCost", 0) or 0
    cost_billions = round(cost_millions / 1000, 2)

    deaths = event.get("deaths", 0) or 0

    econ_events.append({
        "event_name": name,
        "storm_name_clean": clean_name,
        "year": year,
        "begin_date": beg,
        "end_date": end,
        "cost_usd_billion_cpi_adjusted": cost_billions,
        "deaths": deaths,
    })

econ_df = pd.DataFrame(econ_events)
print(f"  Total tropical cyclone economic events: {len(econ_df)}")
if not econ_df.empty:
    print(f"  Year range: {econ_df['year'].min()} to {econ_df['year'].max()}")
    print(f"  Total CPI-adjusted cost: ${econ_df['cost_usd_billion_cpi_adjusted'].sum():.1f}B")

# 4d. Merge hurricane track data with economic data on (storm_name, year)
print("\n--- Merging hurricane tracks with economic impacts ---")
if not florida_storms_df.empty and not econ_df.empty:
    # Create merge keys
    florida_storms_df["_merge_name"] = florida_storms_df["storm_name"].str.upper().str.strip()
    econ_df["_merge_name"] = econ_df["storm_name_clean"].str.strip()

    hurricane_econ = econ_df.merge(
        florida_storms_df[["_merge_name", "year", "closest_distance_nm", "max_wind_kt", "min_pressure_mb", "has_florida_landfall"]],
        on=["_merge_name", "year"],
        how="inner",
    )
    hurricane_econ = hurricane_econ.drop(columns=["_merge_name", "storm_name_clean"])
    print(f"  Matched events (inner join on name+year): {len(hurricane_econ)}")
else:
    hurricane_econ = pd.DataFrame()
    print("  WARNING: No hurricane or economic data available for merge")

# Save merged hurricane-economic data to processed/
if not hurricane_econ.empty:
    hurricane_id_cols = ["event_name", "year", "begin_date", "end_date"]
    hurricane_value_cols = [c for c in hurricane_econ.columns if c not in hurricane_id_cols]
    hurricane_econ_long = hurricane_econ.melt(
        id_vars=hurricane_id_cols,
        value_vars=hurricane_value_cols,
        var_name="metric",
        value_name="value",
    )
    hurricane_long_path = PROCESSED_DATA_DIR / "florida_hurricane_economic_merged_long.csv"
    hurricane_legacy_path = PROCESSED_DATA_DIR / "florida_hurricane_economic_merged.csv"
    hurricane_econ_long.to_csv(hurricane_long_path, index=False)
    # Keep legacy filename for backward compatibility; file content is long-format.
    hurricane_econ_long.to_csv(hurricane_legacy_path, index=False)
    print(f"  Saved: data/processed/florida_hurricane_economic_merged_long.csv")
    print(f"  Saved: data/processed/florida_hurricane_economic_merged.csv (legacy long-format alias)")
    print(f"\n  Merged hurricane-economic data:")
    print(hurricane_econ_long.head(20).to_string(index=False))


# =============================================================================
# Section 5: Merge primary + supplementary data
# =============================================================================

print("\n" + "=" * 70)
print("SECTION 5: Merge Primary (Zillow) + Supplementary (Hurricane) Data")
print("=" * 70)

# The Zillow data is in strict long format (Metro × Month × metric).
# Hurricane/economic signals are year-level, so we create year-level long rows
# and expand them to each Metro × Month via year matching.

# 5a. Create annual hurricane summary for Florida
print("\n--- Building annual hurricane summary ---")
if not florida_storms_df.empty:
    annual_hurricane = florida_storms_df.groupby("year").agg(
        hurricane_count=("storm_id", "count"),
        hurricane_max_wind_kt=("max_wind_kt", "max"),
        hurricane_min_pressure_mb=("min_pressure_mb", "min"),
        hurricane_closest_nm=("closest_distance_nm", "min"),
    ).reset_index()
    annual_hurricane = annual_hurricane.rename(columns={"year": "hurricane_year"})
    print(f"  Annual summary: {len(annual_hurricane)} years with storm activity")
    print(annual_hurricane.to_string(index=False))
else:
    annual_hurricane = pd.DataFrame(columns=[
        "hurricane_year", "hurricane_count", "hurricane_max_wind_kt",
        "hurricane_min_pressure_mb", "hurricane_closest_nm",
    ])

# 5b. Add annual economic impact summary
if not hurricane_econ.empty and "year" in hurricane_econ.columns:
    annual_econ = hurricane_econ.groupby("year").agg(
        hurricane_total_cost_billion=("cost_usd_billion_cpi_adjusted", "sum"),
        hurricane_total_deaths=("deaths", "sum"),
    ).reset_index()
    annual_econ = annual_econ.rename(columns={"year": "hurricane_year"})

    annual_hurricane = annual_hurricane.merge(annual_econ, on="hurricane_year", how="left")
    annual_hurricane["hurricane_total_cost_billion"] = annual_hurricane["hurricane_total_cost_billion"].fillna(0)
    annual_hurricane["hurricane_total_deaths"] = annual_hurricane["hurricane_total_deaths"].fillna(0).astype(int)

# 5c. Build Metro × Month key table and attach year
panel_keys = zillow_panel[["Metro", "Date"]].drop_duplicates().copy()

# Option 1 (balanced panel): keep only dates shared by all metros.
# This enforces equal time observations per entity for panel methods.
common_dates = (
    panel_keys.groupby("Date")["Metro"]
    .nunique()
    .loc[lambda s: s == panel_keys["Metro"].nunique()]
    .index
)
panel_keys = panel_keys[panel_keys["Date"].isin(common_dates)].copy()
zillow_panel = zillow_panel[zillow_panel["Date"].isin(common_dates)].copy()

print(f"  Balanced date support: {len(common_dates)} months shared by all metros")
if len(common_dates) > 0:
    print(f"  Balanced date range: {min(common_dates).date()} to {max(common_dates).date()}")

panel_keys["hurricane_year"] = panel_keys["Date"].dt.year

# 5d. Convert annual hurricane/econ summaries to long metric/value rows
hurricane_metric_cols = [c for c in annual_hurricane.columns if c != "hurricane_year"]
annual_hurricane_long = annual_hurricane.melt(
    id_vars=["hurricane_year"],
    value_vars=hurricane_metric_cols,
    var_name="metric",
    value_name="value",
)

# 5e. Expand year-level hurricane metrics to each Metro × Month row.
# Build a complete year×metric scaffold first so missing years still retain
# explicit metric names with zero values.
year_metric_scaffold = pd.MultiIndex.from_product(
    [sorted(panel_keys["hurricane_year"].unique()), hurricane_metric_cols],
    names=["hurricane_year", "metric"],
).to_frame(index=False)
year_metric_values = year_metric_scaffold.merge(
    annual_hurricane_long,
    on=["hurricane_year", "metric"],
    how="left",
)
year_metric_values["value"] = year_metric_values["value"].fillna(0)

hurricane_long = panel_keys.merge(year_metric_values, on="hurricane_year", how="left")
hurricane_long = hurricane_long[["Metro", "Date", "metric", "value"]]

# 5f. Combine housing long data + hurricane long data
n_before_merge = len(zillow_panel)
merged = pd.concat([zillow_panel[["Metro", "Date", "metric", "value"]], hurricane_long], ignore_index=True)
n_after_merge = len(merged)
print(f"\n--- Merge verification ---")
print(f"  Zillow long rows before merge:  {n_before_merge}")
print(f"  Combined long rows after merge: {n_after_merge}")
print(f"  Added hurricane/economic rows:  {n_after_merge - n_before_merge}")


# =============================================================================
# Section 6: Reshape to panel structure (Entity × Time)
# =============================================================================

print("\n" + "=" * 70)
print("SECTION 6: Reshape to Panel Structure (Entity × Time)")
print("=" * 70)

# The data is in strict long format (one row per Metro × Date × metric).
# Verify panel structure and document dimensions.

panel = merged.copy()

# 6a. Set entity and time variables
entity_var = "Metro"
time_var = "Date"

# 6b. Format Date as YYYY-MM-DD string for output (already datetime from Section 3)
panel["Date"] = panel["Date"].dt.strftime("%Y-%m-%d")

# 6c. Ensure no missing keys
assert panel[entity_var].notna().all(), "Found null entity IDs (Metro)!"
assert panel[time_var].notna().all(), "Found null time values (Date)!"
print(f"  ✓ No missing keys: {entity_var} and {time_var} are 100% non-null")

# 6d. Sort by entity, then time
panel = panel.sort_values([entity_var, time_var]).reset_index(drop=True)

# 6e. Panel dimensions
n_entities = panel[entity_var].nunique()
n_periods = panel[time_var].nunique()
n_obs = len(panel)
entity_time = panel[[entity_var, time_var]].drop_duplicates()
obs_per_entity = entity_time.groupby(entity_var)[time_var].count()
obs_per_entity_metric = panel.groupby([entity_var, "metric"])[time_var].count()
balanced = "balanced" if obs_per_entity.min() == obs_per_entity.max() else "unbalanced"

print(f"\n--- Panel structure ---")
print(f"  Entity variable: {entity_var} (Florida MSA name)")
print(f"  Time variable:   {time_var} (monthly, YYYY-MM-DD)")
print(f"  Panel type:      {balanced}")
print(f"  Entities:        {n_entities}")
print(f"  Time periods:    {n_periods}")
print(f"  Observations:    {n_obs}")
print(f"  Obs per entity:  min={obs_per_entity.min()}, max={obs_per_entity.max()}")
print(f"  Metrics:         {panel['metric'].nunique()}")
print(f"  Obs per entity×metric: min={obs_per_entity_metric.min()}, max={obs_per_entity_metric.max()}")

# 6f. Sample statistics
print(f"\n--- Sample statistics ---")
stats = panel.groupby("metric")["value"].agg(["mean", "std", "min", "max"])
stats["missing_n"] = panel.groupby("metric")["value"].apply(lambda s: s.isnull().sum())
stats["missing_pct"] = panel.groupby("metric")["value"].apply(lambda s: round(100 * s.isnull().mean(), 1))
stats = stats.rename(columns={"mean": "Mean", "std": "Std", "min": "Min", "max": "Max",
                                "missing_n": "Missing (N)", "missing_pct": "Missing (%)"})
print(stats.to_string())


# =============================================================================
# Section 7: Save tidy output and metadata
# =============================================================================

print("\n" + "=" * 70)
print("SECTION 7: Save Tidy Output and Metadata")
print("=" * 70)

# 7a. Save strict long-format master dataset CSV
output_csv = FINAL_DATA_DIR / "housing_master_dataset_long.csv"
panel.to_csv(output_csv, index=False, encoding="utf-8")
print(f"\n  ✓ Saved: {output_csv.relative_to(PROJECT_ROOT)}")
print(f"    {n_obs} rows × {len(panel.columns)} columns")

# Keep legacy filename for backward compatibility, but now in long format.
legacy_output_csv = FINAL_DATA_DIR / "housing_analysis_panel.csv"
panel.to_csv(legacy_output_csv, index=False, encoding="utf-8")
print(f"  ✓ Saved: {legacy_output_csv.relative_to(PROJECT_ROOT)} (long format)")

# 7b. Build and save metadata JSON
metadata = {
    "dataset": "Housing — Florida Hurricane Exposure & Housing Market",
    "team": "1st Row Team",
    "members": ["Nevaeh Marquez", "Logan Ledbetter", "Raleigh Elizabeth Wullkotte", "Sam Bronner"],
    "date_created": "2026-02-20",
    "entity_variable": entity_var,
    "time_variable": time_var,
    "panel_type": balanced,
    "n_entities": int(n_entities),
    "n_time_periods": int(n_periods),
    "n_obs": int(n_obs),
    "time_range": f"{panel[time_var].min()} to {panel[time_var].max()}",
    "variables": list(panel.columns),
    "schema": "long",
    "long_schema": {
        "id_columns": ["Metro", "Date", "metric"],
        "value_column": "value",
    },
    "primary_sources": {
        "zillow": {
            "description": "Zillow Research metro-level housing indicators",
            "metrics": sorted_metrics,
            "url_base": "https://files.zillowstatic.com/research/public_csvs/",
        },
        "hurdat2": {
            "description": "NOAA/NHC HURDAT2 Atlantic hurricane track data",
            "url": hurdat2_url,
        },
        "noaa_economic": {
            "description": "NOAA NCEI Billion-Dollar Disaster events (tropical cyclones, CPI-adjusted)",
            "url": NOAA_ECON_URL,
        },
    },
    "cleaning_decisions": {
        "missing_metrics": "Rows with null values in long schema are dropped.",
        "outliers": "Metric-specific values winsorized at 1st/99th percentiles in long format.",
        "duplicates": "Duplicate Metro×Date×metric rows dropped, keeping first occurrence.",
        "hurricane_fill": "Years with no Florida-proximity hurricane activity filled with zeros for hurricane columns.",
        "geographic_filter": "Zillow data filtered to Florida MSAs only (StateName='FL', RegionType='msa').",
        "storm_proximity_filter": f"HURDAT2 tracks filtered to storms within {FL_PROXIMITY_NM} NM of Florida center ({FL_CENTER_LAT}°N, {abs(FL_CENTER_LON)}°W), years 2000–2025.",
    },
}

output_json = FINAL_DATA_DIR / "housing_metadata.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, default=str)
print(f"  ✓ Saved: {output_json.relative_to(PROJECT_ROOT)}")

# 7c. Save long-form data dictionary
data_dictionary_rows = [
    {
        "dataset": "housing_master_dataset_long",
        "column_name": "Metro",
        "data_type": "string",
        "role": "identifier",
        "description": "Florida metropolitan statistical area name.",
    },
    {
        "dataset": "housing_master_dataset_long",
        "column_name": "Date",
        "data_type": "date (YYYY-MM-DD)",
        "role": "time",
        "description": "Monthly observation date.",
    },
    {
        "dataset": "housing_master_dataset_long",
        "column_name": "metric",
        "data_type": "string",
        "role": "measure name",
        "description": "Metric label (housing or hurricane/economic indicator).",
    },
    {
        "dataset": "housing_master_dataset_long",
        "column_name": "value",
        "data_type": "numeric",
        "role": "measure value",
        "description": "Observed value for the metric at Metro and Date.",
    },
    {
        "dataset": "florida_hurricane_economic_merged_long",
        "column_name": "event_name",
        "data_type": "string",
        "role": "identifier",
        "description": "NOAA tropical cyclone event label.",
    },
    {
        "dataset": "florida_hurricane_economic_merged_long",
        "column_name": "year",
        "data_type": "integer",
        "role": "time",
        "description": "Calendar year of the hurricane event.",
    },
    {
        "dataset": "florida_hurricane_economic_merged_long",
        "column_name": "begin_date",
        "data_type": "string (YYYYMMDD)",
        "role": "event date",
        "description": "Event start date from NOAA Billion-Dollar dataset.",
    },
    {
        "dataset": "florida_hurricane_economic_merged_long",
        "column_name": "end_date",
        "data_type": "string (YYYYMMDD)",
        "role": "event date",
        "description": "Event end date from NOAA Billion-Dollar dataset.",
    },
    {
        "dataset": "florida_hurricane_economic_merged_long",
        "column_name": "metric",
        "data_type": "string",
        "role": "measure name",
        "description": "Hurricane/economic metric label for the event.",
    },
    {
        "dataset": "florida_hurricane_economic_merged_long",
        "column_name": "value",
        "data_type": "numeric|boolean",
        "role": "measure value",
        "description": "Observed value for the event-level metric.",
    },
    {
        "dataset": "florida_storms_60nm_2000_2025_long",
        "column_name": "storm_id",
        "data_type": "string",
        "role": "identifier",
        "description": "HURDAT2 storm identifier.",
    },
    {
        "dataset": "florida_storms_60nm_2000_2025_long",
        "column_name": "storm_name",
        "data_type": "string",
        "role": "identifier",
        "description": "Storm name from HURDAT2.",
    },
    {
        "dataset": "florida_storms_60nm_2000_2025_long",
        "column_name": "year",
        "data_type": "integer",
        "role": "time",
        "description": "Calendar year of the storm record.",
    },
    {
        "dataset": "florida_storms_60nm_2000_2025_long",
        "column_name": "metric",
        "data_type": "string",
        "role": "measure name",
        "description": "Storm-level metric label for the processed output.",
    },
    {
        "dataset": "florida_storms_60nm_2000_2025_long",
        "column_name": "value",
        "data_type": "numeric|boolean",
        "role": "measure value",
        "description": "Observed value for the storm-level metric.",
    },
]
data_dictionary_df = pd.DataFrame(data_dictionary_rows)
data_dictionary_path = FINAL_DATA_DIR / "housing_data_dictionary_long.csv"
data_dictionary_df.to_csv(data_dictionary_path, index=False, encoding="utf-8")
print(f"  ✓ Saved: {data_dictionary_path.relative_to(PROJECT_ROOT)}")

# 7d. Final confirmation
print(f"\n{'=' * 70}")
print(f"PIPELINE COMPLETE")
print(f"{'=' * 70}")
print(f"  Output files:")
print(f"    1. {output_csv.relative_to(PROJECT_ROOT)} ({n_obs} rows × {len(panel.columns)} cols)")
print(f"    2. {legacy_output_csv.relative_to(PROJECT_ROOT)} ({n_obs} rows × {len(panel.columns)} cols)")
print(f"    3. {output_json.relative_to(PROJECT_ROOT)}")
print(f"    4. {data_dictionary_path.relative_to(PROJECT_ROOT)}")
print(f"  Panel: {n_entities} metros × {n_periods} months = {n_obs} observations ({balanced})")
print(f"  Variables: {list(panel.columns)}")
