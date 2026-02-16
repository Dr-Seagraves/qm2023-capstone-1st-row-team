#!/usr/bin/env python3
"""
Reproduce Zillow Data Processing Pipeline
===========================================

This script reproduces the complete Zillow data processing pipeline:
1. Reads data source URLs from config/dataset_sources.txt
2. Downloads all Zillow datasets to data/raw/
3. Filters to Florida metropolitan areas
4. Consolidates multiple metrics into processed format
5. Saves consolidated output to data/processed/florida_zillow_metrics_monthly.csv

Usage:
    python reproduce_zillow_processing.py           # Run full pipeline
    python reproduce_zillow_processing.py --help    # Show options

Author: Capstone Team
Date: 2026
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import urlparse

from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR, CONFIG_DIR


def read_sources(sources_file: Path) -> list[str]:
    """
    Read data source URLs from config file.
    
    Args:
        sources_file: Path to config/dataset_sources.txt
        
    Returns:
        List of URLs to download
    """
    if not sources_file.exists():
        raise FileNotFoundError(f"Sources file not found: {sources_file}")

    urls: list[str] = []
    for line in sources_file.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        urls.append(cleaned)
    return urls


def filename_from_url(url: str) -> str:
    """
    Extract filename from URL, removing query parameters.
    
    Args:
        url: Complete URL with potential query string
        
    Returns:
        Filename suitable for saving
    """
    parsed = urlparse(url)
    # Remove query parameters
    path = parsed.path.split('?')[0]
    name = os.path.basename(path)
    return name if name else "data.csv"


def download_if_needed(url: str, dest_dir: Path, verbose: bool = True) -> Path | None:
    """
    Download file if not already present.
    
    Args:
        url: URL to download
        dest_dir: Directory to save file
        verbose: Print status messages
        
    Returns:
        Path to downloaded file, or None if download failed
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = filename_from_url(url)
    dest_path = dest_dir / filename

    if dest_path.exists():
        if verbose:
            print(f"  ✓ {filename} (already present)")
        return dest_path

    try:
        if verbose:
            print(f"  Downloading {filename}...")
        urlretrieve(url, dest_path)
        if verbose:
            print(f"  ✓ {filename}")
        return dest_path
    except Exception as e:
        if verbose:
            print(f"  ✗ Error downloading {filename}: {e}")
        return None


def process_zillow_file(csv_path: Path, metric_name: str, verbose: bool = False) -> dict:
    """
    Process a Zillow CSV file and filter to Florida metro areas.
    
    Args:
        csv_path: Path to Zillow CSV file
        metric_name: Name of the metric (for output identification)
        verbose: Print debug messages
        
    Returns:
        Dictionary mapping florida_metro -> {date -> (metric, value)}
    """
    if not csv_path.exists():
        if verbose:
            print(f"Warning: File not found: {csv_path}")
        return {}
    
    florida_data = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if reader.fieldnames is None:
                if verbose:
                    print(f"Warning: {csv_path.name} has no header")
                return {}
            
            # First 5 columns are typically metadata
            metadata_cols = {'RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName'}
            date_columns = [col for col in reader.fieldnames if col not in metadata_cols]
            
            for row in reader:
                # Filter to Florida metros
                state = row.get('StateName', '')
                region_type = row.get('RegionType', '')
                
                if state != 'FL' or region_type != 'msa':
                    continue
                
                metro_name = row.get('RegionName', '')
                if not metro_name:
                    continue
                
                if metro_name not in florida_data:
                    florida_data[metro_name] = {}
                
                # Extract values for each date
                for date_str in date_columns:
                    try:
                        value = float(row[date_str])
                        florida_data[metro_name][date_str] = (metric_name, value)
                    except (ValueError, KeyError):
                        pass
    except Exception as e:
        if verbose:
            print(f"Error processing {csv_path}: {e}")
    
    return florida_data


def main(
    skip_download: bool = False,
    verbose: bool = False,
    output_file: str | None = None,
) -> None:
    """
    Main pipeline: download sources, process Zillow data, save results.
    
    Args:
        skip_download: If True, use existing files in data/raw/
        verbose: Print verbose debug output
        output_file: Custom output filename (default: florida_zillow_metrics_monthly.csv)
    """
    print("\n" + "=" * 70)
    print("ZILLOW DATA PROCESSING PIPELINE")
    print("=" * 70)
    
    # Read sources from config
    sources_file = CONFIG_DIR / "dataset_sources.txt"
    urls = read_sources(sources_file)
    print(f"\n📋 Found {len(urls)} data sources in {sources_file}")
    
    # Download files
    if not skip_download:
        print(f"\n📥 Downloading Zillow datasets ({len(urls)} sources)...")
        downloaded_files = []
        for i, url in enumerate(urls, 1):
            result = download_if_needed(url, RAW_DATA_DIR, verbose=True)
            if result:
                downloaded_files.append(result)
    else:
        print("\n⏭️  Skipping downloads (--skip-download)")
        # Find CSV files in raw directory
        downloaded_files = list(RAW_DATA_DIR.glob("*.csv"))
        print(f"Found {len(downloaded_files)} CSV files in {RAW_DATA_DIR}")
    
    print(f"\n📊 Processing {len(downloaded_files)} files...")
    
    # Map filenames to metric names for output
    metric_mapping = {
        'Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv': 'ZHVI',
        'State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv': 'ZHVI_State',
        'Metro_zhvf_growth_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv': 'ZHVF_Growth',
        'Metro_zori_uc_sfrcondomfr_sm_month.csv': 'ZORI',
        'National_zorf_growth_uc_sfr_sm_month.csv': 'ZORF_Growth',
        'Metro_invt_fs_uc_sfrcondo_sm_month.csv': 'Inventory',
        'Metro_sales_count_now_uc_sfrcondo_month.csv': 'Sales_Count',
        'Metro_mean_doz_pending_uc_sfrcondo_sm_month.csv': 'Days_on_Market',
        'Metro_market_temp_index_uc_sfrcondo_month.csv': 'Market_Temp',
        'Metro_new_con_sales_count_raw_uc_sfrcondo_month.csv': 'New_Construction',
        'Metro_new_homeowner_income_needed_downpayment_0.20_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv': 'Income_Needed',
    }
    
    all_florida_data = {}
    
    # Process each downloaded file
    for csv_path in sorted(downloaded_files):
        metric = metric_mapping.get(csv_path.name, csv_path.stem)
        print(f"  Processing {csv_path.name} ({metric})...", end=" ")
        florida_data = process_zillow_file(csv_path, metric, verbose=verbose)
        
        if florida_data:
            print(f"✓ {len(florida_data)} metros")
            # Merge data
            for metro, data in florida_data.items():
                if metro not in all_florida_data:
                    all_florida_data[metro] = {}
                all_florida_data[metro].update(data)
        else:
            print("✗ No Florida metros found")
    
    if not all_florida_data:
        print("\n❌ Error: No Florida metro data found")
        return
    
    # Write consolidated output
    output_filename = output_file or "florida_zillow_metrics_monthly.csv"
    output_csv = PROCESSED_DATA_DIR / output_filename
    
    print(f"\n💾 Writing consolidated output...")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Get all metrics and dates from data
        all_metrics = set()
        all_dates = set()
        for metro_data in all_florida_data.values():
            for date_str, (metric, _) in metro_data.items():
                all_metrics.add(metric)
                all_dates.add(date_str)
        
        # Write header
        sorted_metrics = sorted(all_metrics)
        sorted_dates = sorted(all_dates)
        writer.writerow(['Metro', 'Date'] + sorted_metrics)
        
        # Write data
        row_count = 0
        for metro_name in sorted(all_florida_data.keys()):
            metro_data = all_florida_data[metro_name]
            for date_str in sorted_dates:
                row_data = [metro_name, date_str]
                for metric in sorted_metrics:
                    # Find value for this metric and date
                    value = None
                    for stored_date, (stored_metric, stored_value) in metro_data.items():
                        if stored_date == date_str and stored_metric == metric:
                            value = stored_value
                            break
                    row_data.append(value if value else '')
                writer.writerow(row_data)
                row_count += 1
    
    # Print results
    print("\n" + "=" * 70)
    print("✅ PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\n📈 Results:")
    print(f"   • Florida metros: {len(all_florida_data)}")
    print(f"   • Metrics included: {len(all_metrics)}")
    print(f"   • Date range: {min(all_dates)} to {max(all_dates)}")
    print(f"   • Total rows: {row_count}")
    print(f"\n📁 Output file:")
    print(f"   {output_csv}")
    print(f"\n🏙️  Florida metros found:")
    for metro in sorted(all_florida_data.keys()):
        print(f"   • {metro}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reproduce Zillow data processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Full pipeline with downloads
  %(prog)s --skip-download    # Use existing files in data/raw/
  %(prog)s --verbose          # Show detailed processing info
        """,
    )
    
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip downloading files; use existing data in data/raw/",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output filename (default: florida_zillow_metrics_monthly.csv)",
    )
    
    args = parser.parse_args()
    
    main(
        skip_download=args.skip_download,
        verbose=args.verbose,
        output_file=args.output,
    )
