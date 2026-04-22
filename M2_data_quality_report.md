# Milestone 2 Data Quality Report

## Quick Summary
Overall, the merged dataset is usable for M3, but a few quality issues can change results if we do not handle them carefully.

## What We Checked in M2
1. We checked summary stats to see if variable ranges looked realistic.
2. We checked correlations between outcome, driver, and controls.
3. We checked time series plots for big jumps, trends, and unusual years.
4. We checked lag patterns to see when hurricane exposure seemed to matter most.
5. We checked group and control variable plots to spot uneven variance and outliers.

## Visual Insights and Economic Meaning
1. The outcome and hurricane related driver moved together in some periods but not evenly across all years.
2. Big periods like the housing crash years and major storm years stood out and could influence model results.
3. Some metros looked more sensitive than others, which suggests possible heterogeneity effects.
4. Control variables showed useful relationships with housing outcomes, so they should stay in M3 specifications.

## Testable Hypotheses for M3
1. **H1 (driver effect):** Higher hurricane exposure is linked to lower short-run housing market growth outcomes in more exposed periods.
2. **H2 (lag effect):** Hurricane exposure has a delayed effect with stronger correlation at short lags (such as 1 to 3 months).
3. **H3 (control effects):** Market controls like rents, inventory, and market temperature explain part of outcome changes and improve model fit.
4. **H4 (heterogeneity):** Effects differ across metro groups, so interaction or subgroup checks are needed.

## Main Data Quality Issues We Found
1. **Missing values:** Several variables are missing a lot of information in early years, especially Inventory, Sales Count, and Days on Market.
2. **Time mismatch:** Hurricane variables are mostly yearly while housing outcomes are monthly.
3. **Outlier periods:** 2008-2012 and major storm years can pull trends strongly.
4. **Heteroskedasticity risk:** Plot patterns suggest nonconstant variance across time and metros.
5. **Multicollinearity risk:** Some hurricane severity measures are strongly related to each other.
6. **Uneven panel coverage:** Some metros have shorter histories, making the panel unbalanced.

## How We Planned to Handle This in M3
1. Use fixed effects to control for metro level and time level differences.
2. Use clustered or robust standard errors.
3. Test alternative lag structures.
4. Run robustness checks that exclude extreme periods.
5. Avoid loading too many highly correlated hurricane measures in one model.
6. Report sample windows and observation counts clearly.

## M2 Outputs We Reviewed
- `code/M2_eda_dashboard.ipynb`
- `results/reports/M2_EDA_summary.md`
- `results/figures/plot1_correlation_heatmap.png`
- `results/figures/plot2_outcome_time_series.png`
- `results/figures/plot3_dual_axis_outcome_vs_driver.png`
- `results/figures/plot4_lagged_effect_analysis.png`
- `results/figures/plot5_group_boxplot_or_alt.png`
- `results/figures/plot6_group_sensitivity_or_alt.png`
- `results/figures/plot7_control_scatter_regplots.png`
- `results/figures/plot8_time_series_decomposition.png`

## Bottom Line
M2 gave us strong visual evidence and clear model ideas for M3. The data has limits, but we identified them early and built a plan to handle them with diagnostics and robustness checks.

## Sign-off

- **Nevaeh Marquez**
- **Logan Ledbetter**
- **River Wullkotte**
- **Sam Bronner**