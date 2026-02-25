# Data Quality Report

Prepared: 2026-02-23

## 1) Scope and Purpose

This report documents data quality for the Florida hurricane and housing market pipeline in this repository, including:

- Data sources (primary and supplementary)
- Cleaning and filtering decisions with before/after counts
- Merge strategy and verification checks
- Final dataset and sample statistics
- Reproducibility checklist
- Ethical considerations and data-loss implications

---

## 2) Data Sources

### Primary Sources

1. **NOAA/NHC HURDAT2 hurricane tracks**  
   - URL registry: [config/dataset_sources.txt](config/dataset_sources.txt)  
   - Fetch script: [code/fetch/fetch_noaa_hurdat2.py](code/fetch/fetch_noaa_hurdat2.py)  
   - Raw file target: `data/raw/hurdat2_raw.txt`

2. **NOAA Billion-Dollar Disaster / Economic Impacts**  
   - URL registry: [config/dataset_sources.txt](config/dataset_sources.txt)  
   - Fetch script: [code/fetch/fetch_noaa_economic_impacts.py](code/fetch/fetch_noaa_economic_impacts.py)  
   - Typical processed inputs: `hurricane_economic_impacts_1980_2024.csv`

3. **Zillow Research housing datasets (metro/state time series)**  
   - URL registry: [config/dataset_sources.txt](config/dataset_sources.txt)  
   - Fetch orchestration: [code/fetch/fetch_all.py](code/fetch/fetch_all.py)  
   - Examples: ZHVI, ZORI, inventory, market temperature, sales count, income needed

### Supplementary / Supporting Sources

- Florida state boundary GeoJSON used to validate in-state hurricane landfalls in [code/filter/filter_florida_landfall_hurricanes.py](code/filter/filter_florida_landfall_hurricanes.py)
- NOAA/NHC index parsing for latest HURDAT2 reference file in [code/filter/filter_florida_landfall_hurricanes.py](code/filter/filter_florida_landfall_hurricanes.py)
- Optional `shapely` usage fallback for geospatial point-in-polygon checks in [code/filter/filter_florida_landfall_hurricanes.py](code/filter/filter_florida_landfall_hurricanes.py)

---

## 3) Cleaning and Filtering Decisions

### A) Zillow scope restriction to Florida MSAs

Rule (in [code/build/build_master.py](code/build/build_master.py)): keep rows where `StateName == "FL"` and `RegionType == "msa"`.

Observed impact across 9 Metro Zillow raw files:

- **Before:** 5,906 rows
- **After:** 223 rows
- **Dropped:** 5,683 rows (**96.23%**)

Interpretation: this is an intentional geographic-focus filter, not random data loss.

### B) HURDAT2 hurricane proximity filter

Rule (in [code/filter/filter_florida_storms_60nm.py](code/filter/filter_florida_storms_60nm.py)):

- Great-circle distance from Florida reference point (27.5, -82.0)
- Keep storms with at least one point within 60 NM
- Restrict years to 2004–2025
- Keep full track records for selected storms within the year range

Observed outputs:

- `florida_storms_60nm_2004_2025.csv`: 5 rows, 11 columns
- `florida_storms_60nm_summary.csv`: 1 row, 6 columns

### C) Economic impact landfall filter

Rule (in [code/filter/filter_florida_landfall_hurricanes.py](code/filter/filter_florida_landfall_hurricanes.py)):

- Keep only events named Hurricane/Tropical Storm
- Match event name + year against HURDAT2 records with record identifier `L` (landfall)
- Confirm landfall location falls within Florida geometry

Observed impact:

- **Before:** 69 rows (`hurricane_economic_impacts_1980_2024.csv`)
- **After:** 22 rows (`hurricane_economic_impacts_1980_2024_florida_landfall.csv`)
- **Dropped:** 47 rows (**68.12%**)

### D) Generic cleaning transforms

From [code/clean/clean_utils.py](code/clean/clean_utils.py), [code/clean/clean_zillow.py](code/clean/clean_zillow.py), [code/clean/clean_economic.py](code/clean/clean_economic.py), [code/clean/clean_hurdat2.py](code/clean/clean_hurdat2.py):

- Standardize column names (lowercase/underscores)
- Drop highly empty rows (`threshold=0.6` Zillow, `0.5` economic)
- Parse numeric/date-like object fields
- Convert dollar strings (`$`, million, billion) to numeric
- Replace sentinel missing values in HURDAT2 (`-99`, `-999`)
- Preserve/ensure wide format for Zillow-style time series

Selected before/after examples from `cleaned_*` files:

- `Metro_mean_doz_pending...`: 676 → 510 (−166)
- `Metro_zori...`: 721 → 353 (−368)
- `Metro_zhvi...`: 895 → 859 (−36)
- `hurricane_economic_impacts_1980_2024.csv`: 69 → 67 (−2)

### Economic justification for cleaning choices

- **Geographic targeting (Florida-only)** improves internal validity for the stated research question (Florida hurricane exposure vs Florida housing metrics).
- **Landfall and proximity filters** reduce measurement error by excluding storms unlikely to affect Florida real estate fundamentals.
- **Dollar normalization** is necessary for interpretable cost comparisons and downstream model scaling.
- **Dropping highly incomplete rows** avoids spurious inference from records without sufficient economic or market signal.

---

## 4) Merge Strategy and Verification

### Implemented strategies

1. **Economic + storm-track merge (keyed enrichment)**  
   Script: [code/merge/merge_hurricane_economic.py](code/merge/merge_hurricane_economic.py)  
   Keying logic: `(storm_name_upper, year)` extracted from `event_name` + `data_year`

2. **Zillow metric consolidation (wide metric union by Metro/Date)**  
   Script: [code/merge/merge_zillow_metrics.py](code/merge/merge_zillow_metrics.py)  
   Output rows represent `Metro × Date`; metric columns are aligned from multiple Zillow files.

3. **Master dataset assembly (config-driven concatenation)**  
   Scripts: [code/merge/merge_all.py](code/merge/merge_all.py), [code/build/build_master.py](code/build/build_master.py)  
   Method: vertical concatenation of enabled datasets with source tagging (`_source_dataset`)

### Verification checks (current outputs)

- `florida_hurricane_economic_merged.csv`: 22 rows, 10 columns
- Track-match coverage within that file:
  - Matched rows with non-null `closest_distance_nm`: **1**
  - Unmatched rows: **21**
- `florida_zillow_metrics_monthly.csv`: 9,164 rows, 13 columns
  - Unique metros: 29
  - Unique dates: 316

Assessment: merge mechanics run successfully, but keyed storm-track enrichment currently has low match yield; this should be treated as a documented data-quality risk for inferential analysis.

---

## 5) Final Dataset Summary and Sample Statistics

### Current final artifact status

- [data/final/master_dataset.csv](data/final/master_dataset.csv) is currently empty (0 rows, 0 columns).
- Reason: the build path is configured to write an empty master dataset when no columns are marked `include: true` in column configuration (see [code/build/build_master.py](code/build/build_master.py)).

### Sample statistics from analysis-ready merged outputs

#### A) `florida_hurricane_economic_merged.csv` (22 rows)

- `cost_usd_billion_cpi_adjusted`: mean 32.55, median 12.00, min 1.10, max 201.30 (n=22)
- `deaths`: mean 42.81, median 28.00, min 1, max 219 (n=21)
- Storm-track numeric coverage fields (`closest_distance_nm`, `max_wind_kt`, `min_pressure_mb`) each currently have n=1 non-null

#### B) `florida_zillow_metrics_monthly.csv` (9,164 rows)

- `ZHVI`: mean 201,065.34, median 170,746.55, min 53,538.83, max 1,001,787.94 (n=8,732)
- `ZORI`: mean 1,517.75, median 1,429.64, min 811.42, max 3,619.60 (n=2,947)
- `Inventory`: mean 5,068.74, median 2,283.50, min 23, max 59,411 (n=2,752)
- `Sales_Count`: mean 3,124.31, median 2,072.00, min 401, max 16,225 (n=1,728)
- `Days_on_Market`: mean 62.76, median 60, min 12, max 258 (n=2,203)
- `Market_Temp`: mean 47.97, median 46, min -37, max 193 (n=2,801)
- `Income_Needed`: mean 60,226.82, median 51,378.30, min 19,757.87, max 172,873.87 (n=3,718)

---

## 6) Reproducibility Checklist

Use this sequence on a clean environment:

1. Install Python dependencies: `python -m pip install -r requirements.txt`
2. Fetch all sources: `python code/fetch/fetch_all.py`
3. Run cleaning: `python code/clean/clean_all.py`
4. Run filters: `python code/filter/filter_all.py`
5. Run merges:
   - `python code/merge/merge_hurricane_economic.py`
   - `python code/merge/merge_zillow_metrics.py`
6. Build final master: `python code/build/build_master.py`
7. Verify outputs exist in:
   - `data/processed/` (intermediate + merged tables)
   - `data/final/master_dataset.csv`
8. Record code and config state:
   - Git commit hash
   - [config/merge_config.json](config/merge_config.json)
   - [config/column_config.json](config/column_config.json)
   - [config/dataset_sources.txt](config/dataset_sources.txt)

Optional dashboard launch for manual QA: `python start.py`

---

## 7) Ethical Considerations: What Data Are We Losing?

1. **Geographic exclusion bias**  
   Florida-only filtering removes non-Florida comparators, which limits external validity and can amplify region-specific confounders.

2. **Event-selection bias**  
   Restricting to Florida landfalls (or 60 NM proximity) excludes near-miss storms that may still influence insurance expectations, migration, or market sentiment.

3. **Temporal scope narrowing**  
   Year filters (e.g., 2004–2025 for proximity output) can suppress long-run baseline variation and understate cyclical effects.

4. **Missingness-induced attrition**  
   Threshold-based row dropping disproportionately removes sparse records, which may represent smaller or less-monitored markets.

5. **Name/year matching limitations in merge**  
   Low match coverage in storm-track enrichment (1/22) indicates potential under-linkage; this can bias estimated relationships toward zero or unstable coefficients.

### Mitigation recommendations

- Maintain an "exclusion ledger" (rows dropped by rule, by dataset).
- Report matched vs unmatched rates for each merge in every model run.
- Run sensitivity analyses with broader storm definitions (e.g., larger distance radius, near-miss categories).
- Preserve untouched snapshots of raw and minimally transformed data for auditability.

---

## 8) Immediate Action Items

1. Improve storm name normalization and fuzzy matching in economic-track merge to raise match yield above current 1/22.
2. Decide/lock `include: true` columns so `master_dataset.csv` is populated.
3. Add automated quality checks (row-count assertions + key uniqueness tests) after each pipeline stage.
