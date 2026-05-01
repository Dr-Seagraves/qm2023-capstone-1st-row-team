# M4 Investment Memo

QM 2023 Capstone Project

Team Members: Nevaeh Marquez, Logan Ledbetter, River Wullkotte, Sam Bronner

Submission Date: May 1, 2026

## Executive Summary

Our fixed-effects analysis shows that hurricane exposure is associated with a statistically significant but heterogeneous response in Florida housing markets. The main interaction term, `storm_x_income_l1`, is positive and significant in the clustered model (coef = 0.0000453, p = 0.0120). The effect is concentrated in metros with higher income needed for home purchase, which suggests that post-storm adjustment is not uniform across Florida.

The safest interpretation is selective caution, not a statewide rule. High-affordability-pressure metros appear more sensitive to storm-related shocks, while lower-income-needed metros show weaker and less stable relationships. The memo recommendations below focus on targeted resilience and buyer support rather than broad market-wide intervention.

## 3.1 Policy Recommendations

Based on our empirical analysis, we provide the following policy recommendations for Florida housing and disaster-resilience policymakers:

### Policy Implication 1: Stabilize Supply in High-Affordability-Pressure Metros

Finding: A 1-unit increase in the lagged hurricane-cost-by-income interaction is associated with higher monthly home-value growth, and the effect is strongest in the high-income-needed subsample (coef = 0.0000514, p = 0.0134).

Recommendation: Prioritize permitting, repair assistance, and insurance-friction relief in metros where affordability pressure is already elevated.

Rationale: When supply is slow to adjust after storms, reconstruction spending and constrained inventory can amplify price pressure. Targeted stabilization can reduce post-disaster volatility and help prevent affordability shocks from concentrating in the same markets.

### Policy Implication 2: Pair Disaster Response with Targeted Buyer Support

Finding: The low-income-needed subsample is not statistically significant (coef = 0.0000202, p = 0.4088), while the main FE result remains robust under clustered standard errors and after excluding March-May 2020.

Recommendation: Direct first-time buyer support, down-payment assistance, and temporary relocation aid toward storm-exposed metros rather than relying on a one-size-fits-all statewide response.

Rationale: The burden of post-storm adjustment falls unevenly across households. Targeted support can help lower-wealth buyers and displaced renters absorb shocks without overstating the effect in less exposed markets.

## 3.2 Scenario Analysis

We model 3 scenarios for the next 12 months based on hurricane-season and insurance-cost expectations:

| Scenario | Driver Change | Predicted Outcome | Impact | Probability |
|---|---|---|---|---:|
| Baseline | Near-average hurricane activity and no major landfalls in core Florida metros | Housing growth stays near trend, with limited cross-metro dispersion | Flat to slightly positive monthly growth | 45% |
| Optimistic | Below-average storm losses and faster repair / insurance processing | Affordability stress eases modestly and housing growth remains stable | About +0.10% monthly growth in exposed metros | 30% |
| Pessimistic | Above-average hurricane losses or a major Florida landfall | Greater volatility and localized price pressure in high-income-needed metros | About -0.25% monthly growth in the most exposed markets | 25% |

Expected value: Weighted average monthly growth impact = (0.45 x 0.00%) + (0.30 x 0.10%) + (0.25 x -0.25%) = -0.01%.

Recommendation: Given asymmetric downside from a severe landfall and the observed concentration of effects in high-affordability-pressure metros, a selective-caution stance is warranted.

## 3.3 Risk Assessment

### Model Risks

1. Stable elasticity assumption: We assume the relationship between lagged hurricane costs and housing outcomes is stable across the sample. If insurance rules, building codes, or migration patterns change materially, the coefficient may drift.
2. Omitted variable bias: Insurance premia, mortgage rates, migration flows, and local zoning or subsidy responses may move with storm exposure and housing demand. If they correlate with the driver, estimated effects may be partly confounded.
3. External validity: The sample is Florida metros over the available panel period. Results may not generalize to states with different coastal structure, insurance markets, or disaster-response regimes.

### Domain-Specific Risks

1. Exposure mismeasurement: Hurricane cost is a state-level annual proxy, not a metro-specific damage measure. That can blur local variation and attenuate true effects.
2. Adaptation over time: Rebuilding standards, insurance withdrawals, and resilience investments can change the relationship between storms and prices over time.
3. Shock overlap: Major macro events like COVID and the housing cycle can interact with hurricane exposure, making the short-run interpretation noisier.

## 3.4 Caveats and Limitations

### Model Limitations

1. Fixed effects assumption: We treat time-invariant metro characteristics as constant. If metros change structure during the sample period, the FE estimates may be biased.
2. Parallel trends for heterogeneity comparisons: The high-vs-low income-needed comparison is not a formal DiD design. We therefore avoid strong causal claims about subgroup differences.
3. Lag specification: We used a 1-month lag based on the M2 EDA and robustness checks. Alternative lags produce similar but not identical estimates, so the true timing may differ by market.
4. Measurement error: Hurricane cost and exposure are measured with coarse proxies relative to local damage. More granular exposure data could change the magnitude of the estimates.

## 3.5 Future Research Directions

To refine this analysis, future work could:

1. Add insurance-premium, mortgage-rate, and migration data to reduce omitted-variable risk and test the channels behind the post-storm price response.
2. Estimate an event-study or difference-in-differences design around major landfalls to test pre-trends and strengthen causal interpretation.
3. Extend the sample to additional states or earlier storm cycles to test whether the Florida pattern generalizes across different market structures.

MEMORANDUM
TO: Investment Committee / Policy Committee / Risk Committee (pick appropriate audience)
FROM: 1st Row Team — Nevaeh Marquez, Logan Ledbetter, River Wullkotte, Sam Bronner
DATE: May 1, 2026
RE: How hurricane exposure relates to Florida housing outcomes — targeted recommendations

Executive Summary
Our two-way fixed-effects analysis of 29 Florida metros (2,012 panel observations) shows a small but statistically robust interaction between prior hurricane economic cost and local affordability pressure. The main interaction term (storm_x_income_l1) is positive and significant in the clustered specification (coef = 0.0000453, p = 0.0120). The effect is concentrated in metros where income needed to buy a home is high, indicating heterogeneity across markets.

Group-level insights and robustness
High-income-needed metros show the clearest positive interaction (coef = 0.0000514, p = 0.0134); low-income-needed metros show a weaker, statistically insignificant effect (coef = 0.0000202, p = 0.4088). The main result is stable to clustered standard errors and to excluding March–May 2020. Alternative specifications (lags, ARIMA forecasting, Random Forest predictive checks) were run; ARIMA did not outperform a naive baseline for aggregate forecasting, and Random Forest had slightly better RMSE than OLS but both had weak out-of-sample fit.

Recommendation (actionable)
Given the current environment, adopt a selective-caution stance: monitor and prioritize resilience and buyer support in high-affordability-pressure metros. Specifically:
- Prioritize permitting, repair assistance, and insurance-friction relief in metros where income-needed is high.
- Pair disaster-response funding with targeted first-time-buyer assistance (down-payment grants, temporary relocation aid) in exposed metros.
- Avoid broad statewide interventions based solely on exposure; instead use the model as a risk screen to flag the most sensitive metros.

Scenario analysis (illustrative)
- Baseline (45%): Near-average storm activity → flat to slightly positive monthly growth.
- Optimistic (30%): Below-average storm losses & faster repairs → ~+0.10% monthly growth in exposed metros.
- Pessimistic (25%): Major landfall or elevated losses → ~-0.25% monthly growth in most exposed metros.
Weighted expected monthly impact (illustrative): about -0.01%.

Risk assessment & caveats
Model risks:
1. Stable-elasticity assumption may break if insurance markets, permitting rules, or migration patterns change.
2. Omitted-variable risk: insurance premia, mortgage-rate shifts, migration flows, and local policy responses could confound estimates.
3. External validity: results are Florida-MSA specific and should not be generalized without re-estimation.

Domain-specific risks:
1. Exposure mismeasurement: hurricane cost is a coarse, state-level proxy; metro-level damage variation is not fully captured.
2. Adaptation over time: resilience investments and insurance market changes can alter relationships.
3. Shock overlap: macro events like COVID can interact with storm effects.

Future research suggestions
1. Add insurance-premium and migration data to test channels.
2. Implement event-study / DiD around major landfalls to strengthen causal claims.
3. Expand to other states or earlier cycles to test external validity.

References (selected)
- Zillow Research (2024). Metro-level housing indicators (ZHVI, ZORI, inventory, etc.). See `config/dataset_sources.txt`.
- NOAA NHC HURDAT2 (2024). Atlantic hurricane track data.
- NOAA NCEI Billion-Dollar Disasters (2024). Tropical cyclone economic cost series.

AI Audit (summary)
We used GitHub Copilot and Claude. The team verified AI outputs by running the pipeline, checking exported tables in `results/tables/`, and matching reported coefficients to `results/reports/M3_interpretation.md`. The team takes full responsibility for final wording and edits.
