[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22639550&assignment_repo_type=AssignmentRepo)
# QM 2023 Capstone Project

Semester-long capstone for Statistics II: Data Analytics.

## Team Members and Roles

> Update role titles as needed for your final submission.

- **Nevaeh Marquez** — Data acquisition and preprocessing
- **Logan-TU** — Pipeline/dashboard engineering and integration
- **Raleigh Elizabeth Wullkotte** — Documentation, QA, and reporting
- **sbronner13** — Supplementary analysis support

## Research Question

How does hurricane activity and landfall exposure in Florida relate to key housing market outcomes (home values, rents, inventory, and market temperature) across Florida MSAs?  
We test whether periods with higher storm intensity or closer proximity are associated with weaker housing market conditions in affected areas.

## Dataset Overview

### Primary sources

- **NOAA/NHC HURDAT2 hurricane tracks**
  - Used for storm paths, wind speed, pressure, and storm-year matching.
- **NOAA economic impact data (billion-dollar disasters)**
  - Used for inflation-adjusted damages and deaths.
- **Zillow Research metro/state time-series files**
  - Used for housing indicators including ZHVI, ZORI, inventory, sales count, days on market, market temperature, and income needed.

### Supplementary sources

- **Florida boundary GeoJSON** for geospatial landfall validation.
- **NOAA/NHC HURDAT index pages** used to locate latest track files.
- Source URL registry is maintained in `config/dataset_sources.txt`.

## Preliminary Hypotheses

1. **H1 (Hurricane exposure and prices):** Greater Florida hurricane exposure is associated with lower short-run home value growth (ZHVI).
2. **H2 (Hurricane exposure and rents):** MSAs with stronger storm exposure experience slower rent growth (ZORI) after major events.
3. **H3 (Market liquidity):** Storm exposure is associated with weaker transaction conditions (higher days on market, lower sales count).
4. **H4 (Supply adjustment):** Following major hurricane periods, active inventory rises in exposed metros due to delayed demand recovery.
5. **H5 (Affordability pressure):** Income needed to purchase homes grows faster in metros where storm risk and rebuilding pressures are higher.

## How to Run the Pipeline (Step-by-Step)

These steps follow the reproducibility sequence in `results/reports/data_quality_report.md`.

1. **Install Python dependencies**

	```bash
	python -m pip install -r requirements.txt
	```

2. **Fetch all source datasets**

	```bash
	python code/fetch/fetch_all.py
	```

3. **Run cleaning scripts**

	```bash
	python code/clean/clean_all.py
	```

4. **Run filtering scripts**

	```bash
	python code/filter/filter_all.py
	```

5. **Run merge scripts**

	```bash
	python code/merge/merge_hurricane_economic.py
	python code/merge/merge_zillow_metrics.py
	```

6. **Build the final master dataset**

	```bash
	python code/build/build_master.py
	```

7. **Verify outputs**

	- Processed data should be in `data/processed/`.
	- Final output should be `data/final/master_dataset.csv`.

8. **(Optional) Launch dashboard**

	```bash
	python start.py
	```

## Project Structure

### Root-level files

- `start.py` / `start.sh` / `start.bat` — launch scripts for the dashboard and API.
- `requirements.txt` — Python dependencies.
- `README.md` — project overview and run instructions.
- `Reproduce Zillow Data.py` — standalone helper script for Zillow data reproduction.

### `code/` (pipeline logic)

This folder contains the full ETL/ELT workflow and utilities.

- `config_paths.py` — centralized filesystem paths used across scripts.
- `logging_config.py` — shared logger setup.
- `fetch_data.py`, `download_hurricane_data.py`, `create_florida_hurricanes_1995_2025.py`, `generate_data_dictionary.py` — helper/legacy utilities.

#### `code/fetch/`

Data acquisition scripts.

- `_fetch_utils.py` — shared URL lookup, download, and caching utilities.
- `fetch_all.py` — runs all fetch scripts in sequence.
- Zillow fetch scripts (`fetch_zillow_*.py`) — pull each housing indicator dataset.
- `fetch_noaa_hurdat2.py` — pulls NOAA HURDAT2 storm-track data.
- `fetch_noaa_economic_impacts.py` — pulls NOAA disaster/economic impact data.

#### `code/clean/`

Data cleaning and normalization.

- `clean_all.py` — orchestration for all cleaning steps.
- `clean_zillow.py` — Zillow-specific cleaning (missingness/type handling).
- `clean_hurdat2.py` — fixed-width/text storm parsing and cleaning.
- `clean_economic.py` — economic data cleaning including dollar parsing.
- `clean_utils.py` — shared utilities (dtype fixes, null checks, reporting, wide-format helpers).

#### `code/filter/`

Sample restriction and domain filters.

- `filter_all.py` — runs all filtering scripts.
- `filter_zillow_florida_msa.py` — keeps Florida metro rows from Zillow files.
- `filter_florida_storms_60nm.py` — keeps storms near Florida using distance rules.
- `filter_florida_landfall_hurricanes.py` — keeps Florida-landfall hurricane economic events.

#### `code/merge/`

Dataset integration logic.

- `merge_hurricane_economic.py` — enriches economic records with storm-track attributes.
- `merge_zillow_metrics.py` — consolidates Zillow metrics by metro/date.
- `merge_all.py` — config-driven multi-dataset merge.
- `merge_hurricane_zillow.py` — placeholder for extended merge methodology.

#### `code/build/`

Final output assembly.

- `build_master.py` — end-to-end build stage (filter + merge + final master output).

### `config/` (runtime configuration)

- `dataset_sources.txt` — source URL registry for fetch scripts.
- `merge_config.json` — merge dataset/column configuration.
- `column_config.json` — selected/included columns for master dataset build.

### `data/` (pipeline data lifecycle)

#### `data/raw/`

Untouched source extracts from Zillow and NOAA. Example files include:

- `Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv`
- `Metro_zori_uc_sfrcondomfr_sm_month.csv`
- `Metro_invt_fs_uc_sfrcondo_sm_month.csv`
- `State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv`
- `events.html`, `data.html` (downloaded source pages)

#### `data/processed/`

Intermediate outputs from cleaning, filtering, and merging.

- `cleaned_*.csv` — cleaned versions of raw/processed inputs.
- `florida_*.csv` — Florida-filtered subsets.
- `florida_storms_60nm_2004_2025.csv`, `florida_storms_60nm_summary.csv` — storm proximity outputs.
- `hurricane_economic_impacts_1980_2024_florida_landfall.csv` — filtered NOAA economic impacts.
- `florida_hurricane_economic_merged.csv` — merged storm + economic table.
- `florida_zillow_metrics_monthly.csv` — consolidated Zillow panel by metro/date.

#### `data/final/`

Final analytics-ready artifacts.

- `master_dataset.csv` — final master file used for analysis/dashboard workflows.
- `data_dictionary.csv`, `data_dictionary.json` — variable definitions and metadata.

### `dashboard/` (interactive app)

- `app.py` — Flask app factory and backend entrypoint.
- `routes/` — API endpoints for charts, pipeline runs, settings, logs, reports, and data APIs.
- `services/` — backend logic (pipeline runner, chart builder, config management, data scanning).
- `frontend/` — Vite + React UI:
	- `src/` — React pages, components, hooks, and styles.
	- `public/satellite/` — static satellite assets.
	- `package.json`, `vite.config.js` — frontend dependencies and build config.

### `results/`

- `results/figures/` — generated plots and figures.
- `results/tables/` — regression/statistical output tables.
- `results/reports/` — written reports (e.g., data quality report).

### `tests/`

- Reserved for test/autograding files (currently minimal in this branch).


