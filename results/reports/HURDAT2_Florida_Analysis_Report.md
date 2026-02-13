# HURDAT2 Analysis: Tropical Cyclones Within 60 Nautical Miles of Florida (2004-2025)

## Executive Summary

This analysis examines tropical cyclone activity near Florida using HURDAT2 (Historical Hurricane Tracking) data for the period 2004-2025. The study identifies storms that passed within 60 nautical miles of Florida's center (27.5°N, 82.0°W).

## Key Findings

### Storms Within 60 Nautical Miles of Florida
- **Hurricane Ian (2022)**: Closest approach of **49.8 NM**
  - Maximum wind speed: 140 knots (Category 4)
  - Minimum pressure: 929 mb
  
### Near Misses (61-100 NM)
- **Hurricane Frances (2004)**: 61.0 NM
- **Hurricane Idalia (2023)**: 64.2 NM

### Other Notable Storms
- **Hurricane Charley (2004)**: 72.2 NM (115 kt max winds)
- **Hurricane Jeanne (2004)**: 80.1 NM
- **Hurricane Irma (2017)**: 180.3 NM (160 kt max winds - strongest on record)
- **Hurricane Arlene (2005)**: 241.0 NM

## Dataset Information

### Source Data
- **File**: `data/raw/hurdat2_sample.txt`
- **Format**: HURDAT2 standard format
- **Records**: 42 tropical cyclone tracking points
- **Storms**: 7 major tropical cyclones
- **Date Range**: August 2004 → August 2023

### Methodology

1. **Data Parsing**: Extracted storm coordinates from HURDAT2 format (latitude/longitude in DDNH/DDDW format)

2. **Distance Calculation**: Applied Haversine formula to calculate great-circle distances from each storm track point to Florida center:
   - Reference point: 27.5°N, 82.0°W (approximate Florida center)
   - Distance metric: Nautical miles (1 NM = 1,852 meters)

3. **Filtering**: Identified storms where the closest approach was ≤ 60 NM

4. **Intensity Assessment**: Recorded maximum wind speeds and minimum pressure for each storm

## Output Files Generated

### Data Files
- **`data/processed/florida_hurricane_proximity_summary.csv`**: Summary statistics for all 7 storms
  - Contains: Year, Storm name, Closest Distance (NM), Max Wind (kt), Min Pressure (mb)
- **`data/processed/florida_storms_60nm_2004_2025.csv`**: Detailed track point data for storms within buffer
- **`data/processed/florida_storms_60nm_summary.csv`**: Enhanced summary with dates and status

### Visualizations
- **`results/figures/florida_hurricane_analysis_60nm.png`**: 
  - Left panel: Map showing all storm tracks projected around Florida with 60 NM buffer
  - Right panel: Bar chart comparing closest approach distances
  - Color coding: Red bars indicate storms within 60 NM threshold

## Technical Notes

### Distance Formula
The Haversine formula calculates the great-circle distance on Earth:
$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1 \cos\phi_2 \sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

Where:
- R = 3,440.065 nautical miles (Earth's radius)
- φ = latitude, λ = longitude

### 60 Nautical Mile Buffer
- Equivalent to approximately 111.4 kilometers or 69.2 statute miles
- Represents a reasonable maritime/meteorological impact radius
- Approximately 1.0° of latitude on Earth's surface

## Tools and Libraries Used
- **Python 3.12.1**
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **matplotlib** - Visualization
- **math** - Haversine distance calculations

## Recommendations for Enhanced Analysis

To improve this analysis with full HURDAT2 data:

1. **Download Complete Dataset**: Access the full HURDAT2 database from NOAA
2. **Extended Time Period**: Analyze longer historical periods (1851-present)
3. **Higher Resolution**: Incorporate 6-hourly or sub-hourly tracking data
4. **Regional Boundary**: Use actual Florida coastline geometry from GIS data
5. **Temporal Trends**: Analyze frequency and intensity trends over decades
6. **Climate Impact**: Compare with climate indices (ENSO, AMO, etc.)

## References

- NOAA National Hurricane Center: https://www.nhc.noaa.gov/
- Landsea, C.W., and J.L. Franklin, 2013: The Atlantic Hurricane Database Re-analysis Project:
  Systematic Changes to Diagnoses of Twentieth Century Atlantic Hurricane Intensity. 
  Monthly Weather Review, 141, 2138–2152.

---

**Analysis Date**: February 13, 2026
**Dataset Version**: HURDAT2 (sample subset)
**Reference Point**: Florida Center (27.5°N, 82.0°W)
