# Milestone 2 Data Quality Report

## Quick Summary
Overall, the merged dataset is usable for M3, but a few quality issues can change results if we do not handle them carefully.

## Main Data Quality Issues
1. **Missing values (biggest issue):** ZORI, Inventory, Days on Market, and Sales Count are missing a lot of early-year observations (mostly before 2018).
2. **Time mismatch:** Hurricane variables are annual, but housing variables are monthly. This makes month-level hurricane timing less precise.
3. **Outlier periods:** 2008-2012 (housing crash) and large storm years (2004, 2022) can dominate trends.
4. **Multicollinearity:** Hurricane cost, wind, and pressure are strongly related, so including all of them together can make coefficients unstable.
5. **Uneven panel coverage:** Some metros have long histories, while smaller metros start later.

## What We Will Do in M3
1. Use ZHVI as the baseline outcome for full-window models.
2. Restrict sparse variables to post-2017 samples and clearly report sample sizes.
3. Add crisis controls and run pre/post-crisis robustness checks.
4. Use one hurricane severity measure at a time (plus PCA as a robustness check).
5. Use robust/clustered standard errors to handle unequal variance and correlated shocks.

## Bottom Line
The data is strong enough for causal modeling in M3, but results should always be reported with sample windows, robustness checks, and clear limits.

## Sign-off

- **Nevaeh Marquez**
- **Logan Ledbetter**
- **River Wullkotte**
- **Sam Bronner**