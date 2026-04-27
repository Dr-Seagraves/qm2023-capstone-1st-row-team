# Final Investment Memo Draft

QM 2023 Capstone Project

Team members: [Insert names]

## Executive Summary

Our fixed-effects analysis finds that hurricane exposure is associated with a statistically significant shift in housing price growth, and the effect is strongest in metros with higher affordability pressure. In the main model, the interaction term between lagged hurricane cost and log income needed is positive and significant (coef = 0.0000453, p = 0.0120), and that result remains stable when we use clustered standard errors, exclude the early COVID period, and test alternative lags.

The practical takeaway is not that every Florida metro reacts the same way. The evidence suggests a selective response: high-income-needed metros show the clearest relationship, while low-income-needed metros are much less responsive. For a non-technical audience, the recommendation is to treat storm exposure as a risk screen rather than a blanket signal and to be more cautious in high-affordability-pressure markets.

## Methodology

### Data sources

This memo combines the team pipeline with external data sources listed in `config/dataset_sources.txt`:

- Zillow metro-level housing indicators: ZHVI, ZORI, inventory, sales count, days on market, market temperature, and income needed.
- NOAA/NHC HURDAT2 hurricane track data.
- NOAA NCEI Billion-Dollar Disasters data for tropical cyclone costs.

### Sample construction

- Cross-sectional unit: 29 Florida metros.
- Main regression sample: 2,012 panel observations.
- Model sample is unbalanced because some housing series begin later than others.
- Outcome used in the main FE model: monthly log ZHVI growth.

### Main model specification

The main regression is a two-way fixed-effects panel model with metro and time fixed effects and clustered standard errors at the metro level.

Outcome:

log(ZHVI_t) growth by metro

Key regressor:

lagged hurricane cost x log(income needed)

Controls:

- log(income needed)
- rent growth
- inventory growth

Model form:

ZHVI_growth_it = beta1 * storm_x_income_l1_it + beta2 * income_log_it + beta3 * zori_growth_it + beta4 * inventory_growth_it + metro FE + time FE + error_it

### Variable definitions

- `storm_x_income_l1`: lagged hurricane cost multiplied by log income needed.
- `income_log`: log of income needed to purchase a home.
- `zori_growth`: monthly log rent growth.
- `inventory_growth`: monthly percent change in inventory.
- `zhvi_growth`: monthly log home-value growth.

### Alternative specifications

- Robustness checks: alternative lags, no-COVID subsample, high-vs-low income-needed subsamples.
- Alternative forecasting benchmark: ARIMA forecast for aggregate ZHVI growth.
- Alternative predictive comparison: OLS vs Random Forest.

## Results

### Table 1. Fixed Effects Regression

| Variable | Baseline FE | Clustered FE | FE No COVID |
|---|---:|---:|---:|
| Storm x Income (t-1) | 0.000045*** | 0.000045** | 0.000045** |
|  | (0.000007) | (0.000018) | (0.000018) |
| log(Income Needed) | -0.004496* | -0.004496 | -0.005379 |
|  | (0.002438) | (0.006113) | (0.006313) |
| Rent Growth | 0.047910*** | 0.047910** | 0.046146** |
|  | (0.008958) | (0.023528) | (0.022720) |
| Inventory Growth | 0.006155*** | 0.006155* | 0.005237 |
|  | (0.002195) | (0.003477) | (0.003594) |
| Entity FE | Yes | Yes | Yes |
| Time FE | Yes | Yes | Yes |
| Clustered SE (Metro) | No | Yes | Yes |
| Observations | 2,012 | 2,012 | 1,949 |

Interpretation: the main coefficient is small in raw units but statistically robust. The sign and significance survive clustered inference and a sample that removes March-May 2020.

### Table 2. Alternative Specification

| Model | Test R2 | RMSE |
|---|---:|---:|
| OLS | -2.6684 | 0.00605 |
| Random Forest | -2.3672 | 0.00580 |

ARIMA summary:

- ADF p-value: 0.5100
- Selected order: (1, 0, 3)
- RMSE ARIMA: 0.00595
- RMSE naive baseline: 0.00257

### Figures

- Figure 1: Key visualization, `../figures/dual_axis_zhvi_vs_hurricane_cost.png`
- Figure 2: Residuals vs fitted, `../figures/M3_residuals_vs_fitted.png`
- Diagnostic appendix figure: `../figures/M3_qq_plot.png`

### Plain-language result statement

The most defensible result is that hurricane exposure matters most where affordability pressure is already high. The high-income-needed subsample stays positive and significant, while the low-income-needed subsample is not statistically significant. That pattern suggests the effect is heterogeneous rather than universal.

## Conclusions and Recommendations

For a housing or policy audience, the safest recommendation is selective caution rather than a broad Florida-wide rule. Higher-income-needed metros appear more sensitive to hurricane-cost shocks, so those markets should be monitored more closely for post-storm pricing and affordability stress. In lower-income-needed metros, the data do not support a strong or consistent effect.

This analysis should not be treated as causal proof of a hurricane-driven price increase or decrease. It is a panel regression with fixed effects and clustered errors, not a fully identified natural experiment. The right use of the result is decision support: it helps flag where storm exposure is more likely to matter, not to predict exact price changes for every market.

## References

Data sources:

- Zillow Research metro CSVs: https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv
- Zillow Research ZORI CSV: https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv
- Zillow Research inventory CSV: https://files.zillowstatic.com/research/public_csvs/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv
- Zillow Research market temperature CSV: https://files.zillowstatic.com/research/public_csvs/market_temp_index/Metro_market_temp_index_uc_sfrcondo_month.csv
- Zillow Research income needed CSV: https://files.zillowstatic.com/research/public_csvs/new_homeowner_income_needed/Metro_new_homeowner_income_needed_downpayment_0.20_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv
- NOAA HURDAT2: https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2024-040425.txt
- NOAA NCEI Billion-Dollar Disasters: https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.json?disasters[]=tropical-cyclone

Add any academic papers cited through Lit-Anchor or Orbis here in APA format.

## Appendix: AI Audit

Use the existing `AI_AUDIT_APPENDIX.md` content and update it to cover M4 drafting work, verification steps, and any final AI-assisted edits used for this memo.
