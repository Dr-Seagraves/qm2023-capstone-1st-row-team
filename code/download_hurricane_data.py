"""
Download and process HURDAT2 hurricane data for storms near Florida (2004-2025)
HURDAT2 data source: https://www.nhc.noaa.gov/data/hurdat2/
"""

import pandas as pd
import numpy as np
from pathlib import Path
import urllib.request
import tempfile
import os
from math import radians, cos, sin, asin, sqrt

# Setup paths
BASE_PATH = Path(__file__).parent.parent
DATA_RAW = BASE_PATH / "data" / "raw"
DATA_PROCESSED = BASE_PATH / "data" / "processed"
DATA_FINAL = BASE_PATH / "data" / "final"

# Ensure directories exist
for path in [DATA_RAW, DATA_PROCESSED, DATA_FINAL]:
    path.mkdir(parents=True, exist_ok=True)

def download_hurdat2():
    """Download HURDAT2 data from NOAA"""
    url = "https://www.nhc.noaa.gov/data/hurdat2/hurdat2.txt"
    output_file = DATA_RAW / "hurdat2_raw.txt"
    
    if output_file.exists():
        print(f"HURDAT2 data already exists at {output_file}")
        return output_file
    
    print(f"Downloading HURDAT2 data from {url}...")
    try:
        urllib.request.urlretrieve(url, output_file)
        print(f"Successfully saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error downloading: {e}")
        return None

def parse_hurdat2(file_path):
    """
    Parse HURDAT2 text file into a DataFrame
    Format: Header lines contain storm info, data lines contain position/intensity
    """
    storms = []
    records = []
    
    with open(file_path, 'r') as f:
        current_storm = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a header line (contains season and storm name)
            if line[0].isalpha():
                # This is a header line
                parts = line.split(',')
                if len(parts) >= 2:
                    current_storm = {
                        'id': parts[0].strip(),
                        'name': parts[1].strip(),
                        'num_records': int(parts[2].strip())
                    }
            else:
                # This is a data line with position and intensity
                if current_storm:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 8:
                        try:
                            record = {
                                'storm_id': current_storm['id'],
                                'storm_name': current_storm['name'],
                                'date': parts[0],
                                'time': parts[1],
                                'record_id': parts[2],
                                'status': parts[3],
                                'lat': float(parts[4][:-1]) * (1 if parts[4][-1] == 'N' else -1),
                                'lon': float(parts[5][:-1]) * (1 if parts[5][-1] == 'E' else -1),
                                'max_wind': int(parts[6]) if parts[6].isdigit() else None,
                                'min_pressure': int(parts[7]) if parts[7].isdigit() else None,
                            }
                            records.append(record)
                        except (ValueError, IndexError):
                            continue
    
    df = pd.DataFrame(records)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df['year'] = df['date'].dt.year
    
    return df

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great circle distance between two points on earth (in nautical miles)
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in nautical miles
    r = 3440.065
    return c * r

def filter_florida_storms(df, max_distance_nm=60):
    """
    Filter storms that came within max_distance_nm of Florida
    Using approximate Florida center: 27.5°N, 82°W
    """
    florida_lat = 27.5
    florida_lon = -82.0
    
    # Calculate distance from Florida for each point
    df['distance_from_florida_nm'] = df.apply(
        lambda row: haversine_distance(florida_lat, florida_lon, row['lat'], row['lon']),
        axis=1
    )
    
    # Find storms that got within max_distance_nm of Florida
    close_storms = df[df['distance_from_florida_nm'] <= max_distance_nm]['storm_id'].unique()
    
    # Filter to storms from 2004-2025
    filtered_df = df[(df['storm_id'].isin(close_storms)) & 
                     (df['year'] >= 2004) & 
                     (df['year'] <= 2025)].copy()
    
    return filtered_df

def main():
    print("=" * 80)
    print("HURDAT2 Data Processing: Florida Storms (2004-2025)")
    print("=" * 80)
    
    # Download data
    hurdat_file = download_hurdat2()
    if not hurdat_file:
        print("Failed to download HURDAT2 data")
        return
    
    # Parse data
    print("\nParsing HURDAT2 data...")
    df = parse_hurdat2(hurdat_file)
    print(f"Total records in HURDAT2: {len(df):,}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Unique storms: {df['storm_id'].nunique()}")
    
    # Filter for Florida storms
    print("\nFiltering for storms within 60 nautical miles of Florida (2004-2025)...")
    florida_storms = filter_florida_storms(df, max_distance_nm=60)
    
    print(f"\nFiltered results:")
    print(f"  Storms affecting Florida area: {florida_storms['storm_id'].nunique()}")
    print(f"  Total records: {len(florida_storms):,}")
    print(f"  Date range: {florida_storms['date'].min()} to {florida_storms['date'].max()}")
    
    # Summary by storm
    print("\n" + "=" * 80)
    print("STORMS WITHIN 60 NM OF FLORIDA (2004-2025)")
    print("=" * 80)
    
    storm_summary = florida_storms.groupby('storm_id').agg({
        'storm_name': 'first',
        'date': ['min', 'max'],
        'year': 'first',
        'max_wind': 'max',
        'min_pressure': 'min',
        'distance_from_florida_nm': 'min'
    }).round(1)
    
    storm_summary.columns = ['Name', 'Start Date', 'End Date', 'Year', 'Max Wind (kt)', 'Min Pressure (mb)', 'Closest Distance (nm)']
    storm_summary = storm_summary.sort_values('Year')
    
    print(storm_summary)
    
    # Save processed data
    output_file = DATA_PROCESSED / "florida_hurricanes_2004_2025.csv"
    florida_storms.to_csv(output_file, index=False)
    print(f"\n✓ Saved filtered data to: {output_file}")
    
    # Save summary
    summary_file = DATA_PROCESSED / "florida_hurricanes_summary.csv"
    storm_summary.to_csv(summary_file)
    print(f"✓ Saved summary to: {summary_file}")
    
    return florida_storms, storm_summary

if __name__ == "__main__":
    florida_storms_df, summary = main()
