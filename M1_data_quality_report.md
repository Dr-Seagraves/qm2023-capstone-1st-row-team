# Milestone 1: Data Quality Report

**Team:** 1st Row Team
**Members:** Nevaeh Marquez, Logan Ledbetter, Raleigh Elizabeth Wullkotte, Sam Bronner
**Date:** 2026-02-20
**Dataset:** Housing — Florida Hurricane Exposure & Housing Market

---

## 1. Data Sources

### Primary: Zillow Research Housing Indicators

- **Source:** Zillow Research public CSV downloads ([zillowstatic.com](https://files.zillowstatic.com/research/public_csvs/))
- **Coverage:** 29 Florida MSAs, monthly frequency, date range varies by metric (2000–2027)
- **Initial row count:** 5,527 rows across 8 Metro-level CSV files (before Florida filter); 197 Florida MSA rows
- **Key variables:** ZHVI (home values), ZORI (rents), Inventory, Sales_Count, Days_on_Market, Market_Temp, Income_Needed, ZHVF_Growth

### Supplementary: NOAA/NHC HURDAT2 Hurricane Tracks

- **Source:** [NHC HURDAT2](https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2024-040425.txt) (auto-detected; filename changes with each NHC release)
- **Variables:** storm_id, storm_name, date, lat, lon, max_wind (kt), min_pressure (mb), record_type
- **Date range:** 1851–2024 (55,230 total track points; filtered to 2000–2025 for Florida-proximity storms → 12 storms)

### Supplementary: NOAA NCEI Billion-Dollar Disasters

- **Source:** [NOAA NCEI API](https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.json?disasters[]=tropical-cyclone)
- **Variables:** event_name, begin_date, end_date, cost_usd_billion_cpi_adjusted, deaths
- **Date range:** 1980–2024 (67 total events, $1,543.0B total CPI-adjusted cost); 7 events matched to Florida-proximity storms

---

## 2. Data Cleaning Decisions

### Per-variable cleaning summary

| Variable | % Missing | Count | Decision | Justification |
|----------|-----------|-------|----------|---------------|
| ZHVI (home values) | 1.0% | 90 / 8,822 | Keep nulls (metric-level) | Coverage varies by MSA; dropping would lose entire metros |
| ZORI (rents) | 66.6% | 5,875 / 8,822 | Keep nulls | ZORI series starts later (~2015); not available for all metros early on |
| Inventory | 68.8% | 6,070 / 8,822 | Keep nulls | Coverage begins mid-2018 for most metros |
| Sales_Count | 80.4% | 7,094 / 8,822 | Keep nulls | Coverage begins late-2019 |
| Days_on_Market | 75.0% | 6,619 / 8,822 | Keep nulls | Coverage begins mid-2018 |
| Market_Temp | 68.2% | 6,021 / 8,822 | Keep nulls | Coverage begins mid-2018 |
| Income_Needed | 57.9% | 5,104 / 8,822 | Keep nulls | Coverage begins late-2017 |
| ZHVF_Growth | 99.0% | 8,735 / 8,822 | Keep nulls | Forecast metric with minimal historical coverage |
| Metro (entity key) | 0% | 0 | — | Non-null for all rows |
| Date (time key) | 0% | 0 | — | Parsed to datetime; unparseable dates dropped |

### Cleaning actions applied

| Decision | Dataset | Rule | Justification |
|----------|---------|------|---------------|
| **Geographic filter** | Zillow | Keep only `StateName == "FL"` and `RegionType == "msa"` | Focus analysis on Florida MSAs per research question |
| **All-null rows** | Zillow panel | Drop rows where every metric column is NaN | No usable data in those observations |
| **Outlier winsorization** | Zillow metrics | Clip at 1st/99th percentile | Cap extreme values while preserving trends; appropriate for housing data |
| **Duplicates** | Zillow panel | `drop_duplicates(subset=["Metro", "Date"], keep="first")` | Ensure one row per entity-time |
| **Date parsing** | Zillow | `pd.to_datetime()` on date columns | Ensure consistent YYYY-MM-DD format for merge alignment |
| **Sentinel values** | HURDAT2 | Replace -999, -99 with NaN | Standard HURDAT2 missing value sentinels |
| **Storm proximity filter** | HURDAT2 tracks | Keep storms within 60 NM of Florida center (27.5°N, 82.0°W), years 2000–2025 | Capture storms with potential Florida market impact |
| **Hurricane-year fill** | Merged panel | Fill years with no storm activity → hurricane columns = 0 | Zero is the correct value (no exposure), not missing |

---

## 3. Merge Strategy

### Join details

1. **Zillow metric consolidation:**
   - All 8 Zillow Metro CSV files pivot from wide to long format, then combine into a single panel on keys `(Metro, Date)`.
   - Join type: outer union across metrics — each metric contributes its own date coverage.
   - Result: one row per Metro × Date with columns for each housing metric.

2. **Hurricane track + economic impact merge:**
   - Join type: inner join on `(storm_name_upper, year)`.
   - Alignment: NOAA NCEI event names parsed to extract storm name; matched against HURDAT2 storm names.
   - Result: Florida-proximity storms enriched with CPI-adjusted cost and death toll data.

3. **Zillow panel + annual hurricane summary:**
   - Annual hurricane summary aggregated from Florida-proximity storms (count, max wind, min pressure, closest distance, total cost, total deaths).
   - Join type: left join on `year` (extracted from Date).
   - Non-hurricane years receive zero-fill.
   - Before/after row counts: identical (left join preserves all Zillow rows).

### Row count verification

- Zillow rows before merge = Zillow rows after merge (asserted in script).
- No accidental duplication: annual hurricane summary has exactly one row per year.

---

## 4. Final Dataset Summary

- **Output file:** `data/final/housing_analysis_panel.csv`
- **Entity variable:** `Metro` (Florida MSA name, e.g., "Tampa-St. Petersburg-Clearwater, FL")
- **Time variable:** `Date` (monthly, YYYY-MM-DD format)
- **Panel type:** Unbalanced (coverage varies by metric and metro)
- **Entities:** 29 Florida MSAs
- **Time periods:** 316 months (2000-01-31 to 2027-01-31)
- **Observations:** 8,822 rows (one row per Metro × Date)

### Sample statistics

| Variable | Mean | Std Dev | Min | Max | Missing (%) |
|----------|------|---------|-----|-----|-------------|
| ZHVI | 198,930.51 | 102,109.39 | 69,606.48 | 604,985.26 | 1.0% |
| ZORI | 1,517.15 | 480.09 | 868.88 | 3,432.46 | 66.6% |
| Inventory | 5,041.64 | 8,684.40 | 40.00 | 53,168.84 | 68.8% |
| Sales_Count | 3,109.05 | 2,653.31 | 552.43 | 11,856.06 | 80.4% |
| Days_on_Market | 62.47 | 28.36 | 16.00 | 156.94 | 75.0% |
| Market_Temp | 47.85 | 19.50 | -13.00 | 133.00 | 68.2% |
| Income_Needed | 60,113.62 | 28,362.24 | 22,852.92 | 146,233.85 | 57.9% |
| ZHVF_Growth | 0.46 | 0.88 | -0.97 | 3.96 | 99.0% |
| hurricane_count | 0.45 | 0.80 | 0 | 3 | 0% |
| hurricane_max_wind_kt | 30.94 | 53.26 | 0 | 155 | 0% |
| hurricane_min_pressure_mb | 285.81 | 436.88 | 0 | 997 | 0% |
| hurricane_closest_nm | 9.87 | 16.83 | 0 | 56.60 | 0% |
| hurricane_total_cost_billion | 10.74 | 28.00 | 0 | 120.71 | 0% |
| hurricane_total_deaths | 15.50 | 40.15 | 0 | 157 | 0% |

*Note:* High missing percentages for some Zillow metrics reflect differing start dates of each time series (e.g., ZORI begins ~2015, Inventory ~2018), not data quality failures. ZHVF_Growth (99% missing) is a forecast metric with minimal historical data and may be excluded from M3 analysis. All statistics above are exact outputs from the pipeline run.

### Data quality flags

- Unbalanced panel: different metrics have different date coverage across MSAs.
- Hurricane columns are zero-filled for non-storm years (not null).
- Hurricane-economic merge relies on exact name matching; some HURDAT2 storm names may differ from NOAA NCEI event names.

---

## 5. Reproducibility Checklist

- [x] Script (`capstone_data_pipeline.py`) runs without errors from top to bottom
- [x] Uses relative paths only (no hardcoded `C:\Users\...` or `/home/...`)
- [x] Output location: `data/final/housing_analysis_panel.csv` and `data/final/housing_metadata.json`
- [x] No manual editing required — script alone produces all outputs
- [x] Metadata JSON saved with dataset summary and cleaning decisions
- [x] AI Audit Appendix (`AI_AUDIT_APPENDIX.md`) complete

### Reproduction steps

```
pip install -r requirements.txt
python capstone_data_pipeline.py
```

Outputs will appear in `data/final/`. Source data is auto-fetched and cached in `data/raw/`.

---

## 6. Ethical Considerations

### What data are we losing?

1. **Geographic exclusion bias:**
   Florida-only filtering removes non-Florida comparators, limiting external validity. Acceptable for our research focus on Florida hurricane exposure; alternative-state comparisons can be explored in M3 robustness checks.

2. **Event-selection bias:**
   The 60 NM proximity filter excludes near-miss storms that may still influence insurance expectations, migration, or market sentiment. By using a proximity threshold rather than landfall-only, we partially mitigate this.

3. **Temporal scope narrowing:**
   Year filters (2000–2025 for storm proximity) suppress long-run baseline variation. Our Zillow data begins around 2000 anyway, so this has minimal practical impact.

4. **Metric coverage gaps:**
   High missing percentages for some metrics (e.g., Sales_Count at 80.4%, ZHVF_Growth at 99.0%) occur because those Zillow series start later or have limited coverage. We preserve these as NaN rather than dropping or imputing, which avoids fabricating data but limits early-period analysis. We will test alternatives in M3 robustness.

5. **Name-matching limitations:**
   Hurricane-economic merge uses exact name matching. Storm names that differ between HURDAT2 and NOAA NCEI (e.g., abbreviations, historical naming conventions) may be missed. This under-linkage could bias hurricane cost associations toward zero.

### Mitigation

- Preserve raw data snapshots for auditability.
- Report matched vs. unmatched rates in pipeline output.
- Run sensitivity analyses with broader storm definitions in M3.
- Document all exclusions with counts in cleaning logs.

---

## Sign-off

- **Nevaeh Marquez**
- **Logan Ledbetter**
- **Raleigh Elizabeth Wullkotte**
- **Sam Bronner**