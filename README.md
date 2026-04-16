# QM 2023 Capstone Project

Semester-long capstone for Statistics II: Data Analytics.

## Team Members and Roles

- **Nevaeh Marquez** — Data acquisition and preprocessing
- **Logan Ledbetter** — Pipeline engineering and integration
- **River Wullkotte** — Documentation, QA, and reporting
- **Sam Bronner** — Supplementary analysis support

## Research Question

How does hurricane activity and landfall exposure in Florida relate to key housing market outcomes (home values, rents, inventory, sales activity, days on market, market temperature, and affordability) across Florida MSAs?

## Dataset Overview

### Primary source

- **Zillow Research metro-level housing indicators**
  - ZHVI (home values), ZORI (rents), inventory, sales count, days on market, market temperature, and income needed.
  - Filtered to Florida MSAs.

### Supplementary sources

- **NOAA/NHC HURDAT2 hurricane tracks** — storm paths, wind speed, pressure, and Florida proximity.
- **NOAA NCEI Billion-Dollar Disasters** — CPI-adjusted economic costs and deaths for tropical cyclone events.
- Source URLs are listed in `config/dataset_sources.txt`.

## Current Progress

1. **Milestone 1 (Complete)**
   - Reproducible data pipeline implemented in `code/capstone_data_pipeline.py`.
   - Data quality documentation completed in `M1_data_quality_report.md`.
   - AI usage disclosure completed in `AI_AUDIT_APPENDIX.md`.

2. **Milestone 2 (Complete)**
   - EDA notebook completed in `code/M2_eda_dashboard.ipynb`.
   - Supplemental visualization script completed in `code/generate_missing_plots.py`.
   - EDA findings and model hypotheses documented in `M2_EDA_summary.md`.

3. **Milestone 3 (Complete)**
   - Econometric models implemented in `code/capstone_models.py`.
   - Required diagnostics and robustness checks completed.
   - Forecasting (ARIMA) and ML comparison (OLS vs Random Forest) completed.
   - Final paper-style regression table exported to `results/tables/M3_regression_table.csv`.
   - Interpretation memo completed in `M3_interpretation.md`.

## Reproducibility From a Clean Clone

This project is reproducible from a fresh clone with one command.

1. **Clone and enter the repository**

```bash
git clone <repo-url>
cd qm2023-capstone-1st-row-team
```

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Run full reproducibility workflow (recommended)**

```bash
python reproduce_all.py
```

This will:
- download/cache raw sources into `data/raw/`
- build final analysis dataset in `data/final/`
- run M3 models and export all figures/tables in `results/`

Notes:
- Internet is required on first run to fetch source datasets.
- Re-runs use cached files in `data/raw/`.
- Set `CAPSTONE_SKIP_PLOTS=1` to skip supplemental M2 figure generation during pipeline execution.

## Step-By-Step Run (Optional)

1. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the pipeline script**

```bash
python code/capstone_data_pipeline.py
```

This single command now builds the final datasets and generates the supplemental M2 plot files in `results/figures/`.

3. **Optional: generate supplemental M2 figures**

```bash
python code/generate_missing_plots.py
```

You can skip plot generation during the main pipeline run by setting `CAPSTONE_SKIP_PLOTS=1`.

4. **Run Milestone 3 models**

```bash
python code/capstone_models.py
```

5. **Optional: open the EDA notebook**

```bash
jupyter notebook code/M2_eda_dashboard.ipynb
```

## Verify Outputs

- `data/processed/` — intermediate cleaned/merged files
- `data/final/` — analysis-ready outputs
- `results/figures/` — generated visualizations
- `results/tables/summary_stats_by_metro.csv` — summary statistics table
- `results/tables/M3_*.csv` — model, diagnostics, robustness, and forecast tables
- `results/tables/M3_regression_table.csv` — final paper-style regression table (main M3 table)
- `results/tables/M3_regression_table_numeric.csv` — machine-readable numeric coefficients/SE/p-values
- `results/figures/M3_*.png` — M3 diagnostic and forecast figures

## Project Structure

```
├── code/
│   ├── capstone_data_pipeline.py     # Main pipeline script (M1)
│   ├── generate_missing_plots.py     # Supplemental M2 plot generation
│   ├── capstone_models.py            # Milestone 3 econometric models
│   ├── reproduce_all.py              # One-command reproducibility workflow
│   └── M2_eda_dashboard.ipynb        # Milestone 2 EDA notebook
├── reproduce_all.py                  # Root wrapper for full workflow
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── M1_data_quality_report.md         # Milestone 1 data quality report
├── M2_data_quality_report.md         # Milestone 2 documentation
├── M3_interpretation.md              # Milestone 3 interpretation memo
├── config/
│   └── dataset_sources.txt           # Source URL registry
├── data/
│   ├── raw/                          # Source files (cached)
│   ├── processed/                    # Intermediate outputs
│   └── final/                        # Final analysis-ready outputs
├── results/
│   ├── figures/                      # Generated plots
│   ├── tables/                       # Statistical output tables
│   └── reports/                      # Written reports (incl. AI_AUDIT_APPENDIX.md and M2_EDA_summary.md)
└── tests/                            # Test/autograding files
```

## Preliminary Hypotheses

1. **H1 (Hurricane exposure and prices):** Greater Florida hurricane exposure is associated with lower short-run home value growth (ZHVI).
2. **H2 (Hurricane exposure and rents):** MSAs with stronger storm exposure experience slower rent growth (ZORI) after major events.
3. **H3 (Market liquidity):** Storm exposure is associated with weaker transaction conditions (higher days on market and lower sales count).
4. **H4 (Supply adjustment):** Following major hurricane periods, active inventory and market temperature dynamics shift in exposed metros.
5. **H5 (Affordability pressure):** Income needed to purchase homes grows faster in metros with higher storm risk exposure.


