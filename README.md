[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22639550&assignment_repo_type=AssignmentRepo)
# QM 2023 Capstone Project

Semester-long capstone for Statistics II: Data Analytics.

## Team Members and Roles

- **Nevaeh Marquez** — Data acquisition and preprocessing
- **Logan Ledbetter** — Pipeline engineering and integration
- **Raleigh Elizabeth Wullkotte** — Documentation, QA, and reporting
- **Sam Bronner** — Supplementary analysis support

## Research Question

How does hurricane activity and landfall exposure in Florida relate to key housing market outcomes (home values, rents, inventory, and market temperature) across Florida MSAs?
We test whether periods with higher storm intensity or closer proximity are associated with weaker housing market conditions in affected areas.

## Dataset Overview

### Primary source

- **Zillow Research metro-level housing indicators**
  - ZHVI (home values), ZORI (rents), inventory, sales count, days on market, market temperature, and income needed.
  - Filtered to Florida MSAs only.

### Supplementary sources

- **NOAA/NHC HURDAT2 hurricane tracks** — storm paths, wind speed, pressure, proximity to Florida.
- **NOAA NCEI Billion-Dollar Disasters** — CPI-adjusted economic costs and deaths for tropical cyclone events.
- Source URLs are listed in `config/dataset_sources.txt`.

## How to Run the Pipeline

1. **Install Python dependencies**

	```bash
	pip install -r requirements.txt
	```

2. **Run the pipeline script**

	```bash
	python code/capstone_data_pipeline.py
	```

3. **Verify outputs**

	- `data/final/housing_analysis_panel.csv` — tidy panel (Metro × Month)
	- `data/final/housing_metadata.json` — dataset metadata and cleaning decisions

The script fetches all data from source URLs (cached after first download), cleans, filters, merges, and saves the final panel. No manual steps are required.

## Project Structure

```
├── code/
│   └── capstone_data_pipeline.py # Main pipeline script (Milestone 1 deliverable)
├── requirements.txt             # Python dependencies (pandas, numpy, requests)
├── README.md                    # This file
├── M1_data_quality_report.md    # Data quality report (Milestone 1 deliverable)
├── AI_AUDIT_APPENDIX.md         # AI usage audit (Milestone 1 deliverable)
├── config/
│   └── dataset_sources.txt      # Source URL registry
├── data/
│   ├── raw/                     # Downloaded source files (auto-fetched, cached)
│   ├── processed/               # Intermediate outputs (storm filter, etc.)
│   └── final/                   # Final outputs
│       ├── housing_analysis_panel.csv   # Tidy analysis panel
│       └── housing_metadata.json        # Dataset metadata
├── results/
│   ├── figures/                 # Generated plots
│   ├── tables/                  # Statistical output tables
│   └── reports/                 # Written reports
└── tests/                       # Test/autograding files
```

## Preliminary Hypotheses

1. **H1 (Hurricane exposure and prices):** Greater Florida hurricane exposure is associated with lower short-run home value growth (ZHVI).
2. **H2 (Hurricane exposure and rents):** MSAs with stronger storm exposure experience slower rent growth (ZORI) after major events.
3. **H3 (Market liquidity):** Storm exposure is associated with weaker transaction conditions (higher days on market, lower sales count).
4. **H4 (Supply adjustment):** Following major hurricane periods, active inventory rises in exposed metros due to delayed demand recovery.
5. **H5 (Affordability pressure):** Income needed to purchase homes grows faster in metros where storm risk and rebuilding pressures are higher.


