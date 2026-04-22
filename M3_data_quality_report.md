# Milestone 3 Data Quality Report

## Quick Summary
Our data was good enough to run the M3 models, but it was not perfect. We found a few issues and handled them with checks so our results are more trustworthy.

## What We Checked
1. We checked for missing values.
2. We checked if variables lined up correctly by month and metro.
3. We checked model assumptions with diagnostics.
4. We checked if results changed under different model choices.

## Main Data Quality Issues We Found
1. **Missing values:** Some housing variables still have lots of missing data in earlier years especially variables that start later.
2. **Time detail mismatch:** Some hurricane inputs are yearly while housing outcomes are monthly, so timing is not perfect.
3. **Uneven metro coverage:** Some Florida metros have longer data histories than others.
4. **Non-constant error spread:** Diagnostics showed heteroskedasticity.
5. **Possible omitted factors:** Things like insurance prices, migration, and local policy changes are not fully captured.

## What We Did About It
1. We used fixed effects to control for metro differences and common time shocks.
2. We used clustered standard errors at the metro level.
3. We ran diagnostics (Breusch-Pagan, VIF, residual plots, Q-Q plot).
4. We ran robustness checks with different lag lengths.
5. We tested results without the March-May 2020 period.
6. We compared subgroup results (high vs low affordability-pressure metros).

## M3 Data Outputs We Reviewed
- `results/tables/M3_regression_table.csv`
- `results/tables/M3_regression_table_numeric.csv`
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

## Bottom Line
The M3 dataset and outputs are strong enough for our analysis goals. We should still be careful with causal claims because of timing limits and possible missing outside factors. We handled all of this by reporting diagnostics, robustness checks, and clear caveats.

## Sign-off

- **Nevaeh Marquez**
- **Logan Ledbetter**
- **River Wullkotte**
- **Sam Bronner**
