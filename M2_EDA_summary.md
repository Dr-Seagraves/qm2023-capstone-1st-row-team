# Milestone 2 — EDA Summary & Findings
**QM 2023 Capstone Project · 1st Row Team**  
Nevaeh Marquez · Logan Ledbetter · Raleigh Elizabeth Wullkotte · Sam Bronner

---

## Key Findings

### 1. **Weak Direct Correlation Between Hurricane Metrics & Home Values**
   - Hurricane cost, wind speed, and pressure show **small-to-moderate correlations** with ZHVI (r ≈ 0.20–0.30), contrary to a priori expectations.
   - **Economic Mechanism:** Florida home values exhibit a strong long-run upward trend (especially post-2012), which may mask or confound the true effect of hurricanes. Aggregate home prices are sticky at monthly frequency; impacts likely operate through transaction volume/market temperature rather than headline price levels.
   - **Implication for M3:** Fixed-effects and difference-in-differences models will be essential to isolate the causal effect from confounding long-term trends.

### 2. **Hurricane Cost Negatively Associated with Inventory (Supply Disruption)**
   - Inventory shows **negative correlation** with hurricane total cost (r ≈ –0.06), consistent with Hypothesis 4 (supply-side disruption).
   - **Economic Mechanism:** Post-hurricane, periods show delayed seller response, causing inventory to fall as properties are removed from market for repairs/assessment. This is a **demand-side confounding factor** for Milestone 3 labor-supply models.
   - **Implication for M3:** Control for lagged inventory in any model of transaction volume to avoid omitted-variable bias.

### 3. **Optimal Lag for Hurricane-ZHVI Relationship ≈ 0 Months (Contemporaneous)**
   - Cross-correlation analysis shows the **strongest correlation at lag 0**, with declining magnitude at longer lags (6, 12 months).
   - **Economic Mechanism:** If effects exist, they occur within the same month as the hurricane event. This is consistent with **immediate investor/market sentiment shocks** rather than gradual rebuilding dynamics.
   - **Implication for M3:** Lag specifications should include contemporaneous hurricane cost; longer lags (3–6 months) show weaker effects and may not be necessary.

### 4. **Housing Volatility Varies by Market Size & Geography**
   - Smaller Florida MSAs (Crestview, Homosassa Springs, Sebastian) exhibit **high ZHVI volatility** (σ > 1.0%).
   - Large metros (Miami, Tampa, Orlando) are **more resilient** (σ < 1.0%), consistent with thicker, more liquid markets absorbing demand shocks better.
   - **Economic Mechanism:** Thick markets have more substitutable housing inventory; thin markets have limited supply options, leading to price swings when demand shifts post-disaster.
   - **Implication for M3:** Consider two-way treatment: exposure (high hurricane cost) × market size (population, liquidity). Allow heterogeneous treatment effects.

### 5. **Strong Seasonal Component in Housing Values**
   - Time-series decompositions show a **clear 12-month seasonal pattern** (e.g., Arcadia: ±200K oscillation around trend).
   - **Economic Mechanism:** Seasonal housing demand (higher in winter months in Florida as retirees migrate) creates predictable valuation swings.
   - **Implication for M3:** Include **seasonal dummies** (month-of-year fixed effects) in all regressions to avoid attributing seasonal price movements to hurricane effects.

### 6. **Co-Movements Suggest Confounding Long-Run Trends**
   - Statewide ZHVI shows **persistent upward trend** (except 2008–2012 financial crisis trough), while hurricane costs spike in discrete years (2004, 2022).
   - The event-study plot reveals **no visible dip in ZHVI at hurricane dates**, suggesting headline home values are insensitive or that the 2008 crisis dominates.
   - **Economic Mechanism:** Long-run structural factors (Florida population growth, amenity demand, historical undervaluation) overwhelm the short-term hurricane shock.
   - **Implication for M3:** Use **metro-level, time-period fixed effects** to difference out these long-run trends; DiD design with treated (high-exposure) vs. control (low-exposure) metros is essential.

---

## Hypotheses for Milestone 3

### **Hypothesis 1: Hurricane Exposure Reduces Short-Term Housing Demand (Transaction Volume)**
   - **Claim:** MSAs with higher hurricane exposure exhibit lower transaction count (Sales_Count), longer Days_on_Market, and weaker Market_Temp in the 0–6 months following a major storm event.
   - **Model Specification:** Panel fixed-effects with lagged hurricane cost as treatment; control for seasonal dummies, Metro FE, Time FE, and lagged inventory.
   - **Expected Sign:** Negative coefficient on lagged hurricane cost → lower Sales_Count, higher Days_on_Market.
   - **Mechanism:** Disaster-exposed buyers postpone purchases; sellers remove properties from market; agents reduce marketing effort. Market temperature (seller advantage index) falls as supply shrinks and demand shifts.

### **Hypothesis 2: Control Premiums for Market Fundamentals (ZORI-ZHVI Linkage)**
   - **Claim:** Rent-to-price ratio (ZORI / ZHVI) serves as a **market efficiency check**. In high-valuation metros (Miami, Tampa), rent growth lags price growth, signaling overvaluation; in low-valuation metros, rents support prices.
   - **Model Specification:** County-level regression with ZORI as outcome, controlling for ZHVI growth, hurricane cost, and metro-level income needed for purchase.
   - **Expected Sign:** Positive coefficient on ZHVI → rent growth follows price growth; large residuals in high-valuation metros indicate speculation.
   - **Mechanism:** Fundamental rental income supports home values. If prices surge while rents stagnate, market may be overheated or driven by investor expectation shifts (e.g., post-hurricane buyup speculation).

### **Hypothesis 3: Heterogeneous Treatment Effects by Market Exposure & Size **
   - **Claim:** Small, highly exposed metros show **larger negative effects** of hurricanes on transaction volume and price stability than large, less exposed metros.
   - **Model Specification:** A three-way interaction DiD: $(Exposure \times Post \times Size)$ where Exposure = decile of mean hurricane cost, Post = indicator for post-2004, Size = metro population quartile.
   - **Expected Sign:** Negative triple-interaction term.
   - **Mechanism:** Thin markets lack buffer inventory; concentrated ownership increases correlation of unit-level shocks; limited creditworthiness of rebuilding buyers post-disaster.

### **Hypothesis 4: Income Needed for Purchase Reflects Disaster Risk Premium**
   - **Claim:** Income_Needed (down payment + monthly obligations) is significantly higher in high-exposure metros, reflecting a **risk premium** required to compensate for hurricane risk.
   - **Model Specification:** Metro-level panel regression with Income_Needed as outcome, treatment = log(mean hurricane_total_cost), controls = ZHVI growth, unemployment, density.
   - **Expected Sign:** Positive coefficient on hurricane cost → higher income barriers in disaster-prone areas.
   - **Mechanism:** Lenders price in default risk post-disaster; insurance costs rise; builders demand higher profit margins in storm zones; affordability deteriorates.

---

## Data Quality Flags & Mitigation Strategies

### **Flag 1: Incomplete Housing Metrics Time Series (Missing Data)**
   - **Issue:** ZORI (65.6%), Inventory (68.8%), Days_on_Market (75.0%), Sales_Count (80.4%) have coverage only from ~2018 onwards. Pre-2018 analysis is severely limited for these variables.
   - **Pattern:** Zillow-provided metrics have inconsistent reporting lags across metros; rural Florida metros are frequently missing.
   - **Mitigation for M3:**
     - Use **ZHVI as primary outcome**, which has only 1% missing.
     - For analyses requiring ZORI/Inventory, restrict sample to post-Dec-2017.
     - Conduct **sensitivity analysis** with and without these incomplete variables to verify robustness.
     - Flag observations with missing data in model output.

### **Flag 2: Hurricane Metrics Are Annual, Not Monthly (Temporal Aggregation)**
   - **Issue:** Hurricane cost and intensity values repeat for all months within a year (e.g., all 2022 months show the same hurricane total cost of ~$120B). This creates **artificial multicollinearity** and reduces monthly-level precision.
   - **Pattern:** Storm intensity/cost is measured annually, but housing transactions are measured monthly, creating a temporal mismatch.
   - **Mitigation for M3:**
     - Use **month-of-first-hurricane-event** as event date (e.g., Ian made landfall Sept 28, 2022 → event marker on 2022-09).
     - Implement **fixed effects on storm month** to isolate exogenous timing variation.
     - Consider **collapsing data to quarterly** frequency to reduce noise from within-year variation.

### **Flag 3: 2008 Financial Crisis Dominates 2004 Hurricane Era (Confounding)**
   - **Issue:** ZHVI crashed ~40% in 2008–2012 (financial crisis) while 2004 hurricane season was followed by 3 years of price growth (2005–2007). **The 2008 crisis overwhelms** any visible hurricane effect.
   - **Pattern:** Event-study plots show ZHVI **rising through major hurricanes** (Charley 2004, Irma 2017) but collapsing during 2008-09, suggesting crisis > hurricane effect.
   - **Mitigation for M3:**
     - Include **crisis indicator** (2008-01 to 2012-12 = 1, else 0) as a control.
     - Run separate DiD models for (i) 2000–2007 (pre-crisis) and (ii) 2013–2024 (post-crisis) to test effect stability.
     - Use **local polynomial smoothing** on ZHVI trend to remove structural breaks before computing residuals.

### **Flag 4: Multicollinearity Among Hurricane Metrics (High Leverage)**
   - **Issue:** Hurricane metrics are highly correlated:
     - Max Wind ↔ Min Pressure (r = 0.87)
     - Max Wind ↔ Total Cost (r = 0.78)  
     - These will inflate standard errors in Milestone 3 models.
   - **Pattern:** Principal Hurricane tracks determine multiple intensity measures; economic cost scales with intensity.
   - **Mitigation for M3:**
     - Use **Principal Component Analysis (PCA)** on hurricane metrics to extract uncorrelated factors (e.g., PC1 = overall storm severity, PC2 = path).
     - Run robustness checks with **single-variable models** (Cost only, Wind only, Pressure only).
     - Report **variance inflation factors (VIF)** in all models; flag VIF > 5.

### **Flag 5: Spatial Autocorrelation in Metro-Level Data (Clustered Errors)**
   - **Issue:** Nearby Florida metros (Miami–Fort Lauderdale, Tampa–St. Petersburg) experience correlated hurricanes and housing market shocks. **OLS standard errors will be underestimated.**
   - **Pattern:** 2004 (Charley, Frances, Jeanne) affected entire state; 2022 Ian primarily South Florida; spatial clustering visible in metro segmentation scatter plot.
   - **Mitigation for M3:**
     - Use **cluster-robust standard errors** (cluster = Coast or Region) in all regressions.
     - Run **spatial models** (SAR / SEM) as robustness check to test for spillover effects between metros.

### **Flag 6: Sample Imbalance & Survival Bias**
   - **Issue:** Metro sample is **not balanced**; some metros have complete 2000–2027 monthly coverage (large metros), while others enter late (e.g., Homosassa Springs may have coverage starting 2010). This creates **unbalanced panel** structure.
   - **Pattern:** Inspection of metro-summary table reveals highly unequal observation counts; rural/small metros have fewer time-periods.
   - **Mitigation for M3:**
     - Explicitly control for **unbalanced structure** using **Mundlak / Hausman test** for fixed effects consistency.
     - Run models on **balanced subsamples** (e.g., metros with ≥180 monthly obs) and report whether results are robust.
     - Include **entry indicator** (if metro appeared before 2010) as a fixed-effect covariate.

---

## Summary Statistics for M3 Model Specification

| Metric | Mean | Std. Dev | Min | Max | Notes |
|--------|------|----------|-----|-----|-------|
| **ZHVI ($)** | 223,400 | 106,500 | 79,200 | 616,000 | Primary outcome; 1% missing. |
| **Hurricane Total Cost ($B)** | 5.2 | 18.4 | 0.0 | 127.0 | Highly right-skewed; consider log or dummy. |
| **Hurricane Count** | 0.22 | 0.44 | 0.0 | 3.0 | Discrete; 78% months have 0 hurricanes. |
| **Sales Count** | 4,200 | 5,100 | 50 | 28,000 | High missingness (80%); use if post-2018 only. |
| **Market Temp** | 35.5 | 24.1 | –50 | 90 | –50 = buyer advantage; +90 = seller advantage. |

---

## Recommended Model for M3 Baseline (Fixed Effects)

```
log(ZHVI_i,t) = β₀ + β₁·log(Hurricane_Cost_i,t) + β₂·Season_t 
                  + FE_i + FE_t + ε_i,t

where:
  - FE_i = Metro fixed effect (absorbs time-invariant metro characteristics)
  - FE_t = Year-Month fixed effect (absorbs economy-wide shocks)
  - Season_t = Month-of-year dummie(seasonal controls)
  - ε_i,t = Cluster-robust error term (cluster = Region)
```

**R&D Extensions:**
1. **Add lags:** Hurricane_{t-1}, {t-2}, ... to test lag structure.
2. **Interaction:** Hurricane_Cost × Exposure_Quartile (for heterogeneity).
3. **DiD:** Compare high-exposure (top 25% cost) vs. low-exposure metros, pre/post major hurricane.
4. **Instrumental Variable:** Use lagged Atlantic SST or NAO index as instrument for hurricane cost (exogenous weather shock).

---

## Data Quality Issues Escalation

| Issue | Severity | Action |
|-------|----------|--------|
| Multicollinearity (hurricane metrics) | Medium | Use PCA; run single-variable models. |
| Spatial autocorrelation | Medium | Use cluster-robust SE; test spatial models. |
| Incomplete ZORI/Inventory series | High | Restrict to post-2017; sensitivity test. |
| 2008 crisis confounding | High | Separate pre/post-crisis analyses; include crisis FE. |
| Unbalanced panel | Low–Medium | Explicit test for fixed-effects consistency. |
| Annual hurricane aggregation | Medium | Use event-date fixed effects; consider quarterly data. |

---

**Next Steps for Milestone 3:**
1. Implement panel OLS, IV, and DiD models using specifications above.
2. Test coefficient stability across subsamples (pre-crisis, post-crisis; by market size; by region).
3. Document all model choices and sensitivity checks in online appendix.
4. Interpret economic magnitude of effects: e.g., "1 std. dev. increase in hurricane cost → X% change in ZHVI."
