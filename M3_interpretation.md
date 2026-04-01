# M3 Interpretation Memo

## 1) Model A Headline Result (Panel FE)

Model A is a two-way fixed-effects model (Metro FE + Time FE) with clustered standard errors at the Metro level.

Headline estimate (Model 2, clustered SE):

- Driver term: `storm_x_income_l1 = hurricane_total_cost_billion_(t-1) * log(Income_Needed)`
- Coefficient: **0.0000453**
- p-value: **0.0120**

Interpretation in economic units:

- A 1-unit increase in the interaction term (higher prior hurricane cost exposure in a higher-affordability-pressure market) is associated with about **0.00453 percentage points** higher monthly log home-value growth, holding Metro and time effects constant.
- Because this is an interaction, the marginal effect of hurricane cost depends on local affordability level (Income_Needed).

Additional controls:

- `zori_growth`: positive and significant (coef 0.0479, p = 0.0419)
- `inventory_growth`: positive but weaker under clustered SE (coef 0.00616, p = 0.0768)
- `income_log`: not statistically significant in clustered FE (p = 0.462)

## 2) Economic Interpretation (Potential Channels)

Possible channels for the positive interaction effect:

1. Risk-capital and rebuilding channel:
Higher-cost storm periods can trigger reconstruction spending and insurance inflows that support prices in markets where buyers already have high income capacity.

2. Supply-friction channel:
Post-storm permitting, repairs, and construction bottlenecks may tighten effective supply, supporting prices in constrained metros.

3. Selection/composition channel:
Higher-income demand may be more resilient after disasters, shifting transaction composition toward higher-value segments.

## 3) Model B Summary

### Option 2: ARIMA Forecast (Aggregate ZHVI Growth)

- ADF test on aggregate monthly ZHVI growth: stat = -1.547, p = 0.510 (fails to reject unit-root at conventional levels).
- Auto-selected ARIMA order: (1, 0, 3)
- 12-step forecast with 95% confidence bands generated.
- Forecast RMSE vs naive baseline:
  - ARIMA RMSE = 0.00595
  - Naive no-change RMSE = 0.00257

Key takeaway:

- In this sample window, ARIMA did **not** outperform a naive no-change baseline for aggregate growth forecasting.

### Option 3: ML Comparison (Random Forest vs OLS)

Test-set performance (time-based split):

- OLS: R² = -2.668, RMSE = 0.00605
- Random Forest: R² = -2.367, RMSE = 0.00580

Key takeaway:

- Random Forest improved RMSE slightly relative to OLS, but both models had weak out-of-sample fit (negative R²).
- This indicates limited predictive signal with current features and sample period.
- Interpretability trade-off remains: OLS is transparent, while Random Forest offers nonlinear flexibility with lower interpretability.

## 4) Diagnostics (Required)

### A) Heteroskedasticity (Breusch-Pagan)

- LM p-value: 1.16e-88
- F p-value: 2.94e-99

Conclusion:

- Strong evidence of heteroskedasticity.
- Corrective action used: clustered standard errors (`cov_type='clustered', cluster_entity=True`).

### B) Multicollinearity (VIF)

- storm_x_income_l1: 1.38
- income_log: 1.53
- zori_growth: 1.27
- inventory_growth: 1.10

Conclusion:

- All VIF values are far below 10.
- No problematic multicollinearity detected in the final FE specification.

### C) Residual Diagnostics

- Residuals vs fitted plot saved: `results/figures/M3_residuals_vs_fitted.png`
- Q-Q plot saved: `results/figures/M3_qq_plot.png`

Interpretation:

- Residual spread is non-constant (consistent with Breusch-Pagan result), reinforcing robust-SE use.
- Q-Q deviations suggest non-normal tails; inference is therefore based on robust clustered errors.

## 5) Robustness Checks (Required)

At least 3 checks were completed (4 total categories):

1. Clustered vs standard SEs:
- Coefficient stable at 0.0000453, while SE rises from 0.00000744 to 0.0000180.
- Significance remains at 5% under clustered SE.

2. Alternative lag structures for driver:
- Lag 1: 0.0000453 (p = 0.0120)
- Lag 2: 0.0000366 (p = 0.0131)
- Lag 3: 0.0000232 (p = 0.0550)
- Pattern: effect attenuates with longer lags.

3. Excluding outlier period (Mar-May 2020):
- Coefficient remains 0.0000453 (p = 0.0114), indicating baseline result is not driven only by early COVID disruption.

4. Group subsamples (high vs low affordability pressure metros):
- High-income-needed metros: 0.0000514 (p = 0.0134)
- Low-income-needed metros: 0.0000202 (p = 0.4088)
- Effect appears concentrated in high affordability-pressure metros.

## 6) Caveats and Identification Limits

1. Omitted variables:
Insurance premia, credit conditions, migration shocks, and local policy responses may confound estimated effects.

2. Driver construction constraints:
Hurricane economic shock data are annual and state-level in this pipeline, so city-specific exposure heterogeneity is limited and captured via interaction terms.

3. Parallel trends (for DiD-style interpretation):
No formal DiD with treated/post indicator is estimated here, so strict parallel-trends claims are not made.

4. External validity:
Results are Florida-MSA specific and should not be generalized to other states without re-estimation.

## 7) Files Produced for M3

- `code/capstone_models.py`
- `results/tables/M3_regression_table.csv`
- `results/tables/M3_diagnostics_summary.csv`
- `results/tables/M3_vif_table.csv`
- `results/tables/M3_robustness_checks.csv`
- `results/tables/M3_arima_summary.csv`
- `results/tables/M3_arima_forecast_vs_naive.csv`
- `results/tables/M3_ml_comparison.csv`
- `results/tables/M3_random_forest_feature_importance.csv`
- `results/figures/M3_residuals_vs_fitted.png`
- `results/figures/M3_qq_plot.png`
- `results/figures/M3_arima_forecast.png`
