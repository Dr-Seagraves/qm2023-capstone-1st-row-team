# Milestone 2 — EDA Summary & Findings
**QM 2023 Capstone Project · 1st Row Team**  
Nevaeh Marquez · Logan Ledbetter · River Wullkotte · Sam Bronner

---

## Key Findings

1. **Correlations are present but not super strong.** Hurricane costs and home values move together a little (around 0.20–0.30), while hurricane costs and inventory are slightly negative (around -0.06). **Economic mechanism:** Florida’s long-term demand can outweigh short-term storm impacts, and after a storm, fewer homes get listed, which tightens supply for a bit.
2. **The biggest effects happen right away (lag 0).** The strongest relationships show up in the same time period, and they fade over time. **Economic mechanism:** People and sellers react quickly (like pulling listings or changing behavior), but home prices are slower to adjust. Also, since the storm data is yearly, the timing is more of a rough estimate than exact.
3. **Smaller cities feel the impact more.** Smaller metro areas seem more volatile and sensitive to shocks compared to bigger ones like Miami, Tampa, or Orlando. **Economic mechanism:** Smaller markets have less activity and fewer alternatives, so any shock hits harder and spreads more easily.
4. **Certain years really skew things.** Big events like the 2008–2012 housing crash or major hurricane years (like 2004 and 2022) can drive a lot of what we see in the data. **Economic mechanism:** Larger economic cycles (like credit and housing crashes) can dominate and mask the effects of hurricanes in overall price trends.
5. **You have to control for other patterns.** Things like seasonality (housing cycles throughout the year), differences between cities, and overall time trends all show up clearly in the data. **Economic mechanism:** Regular patterns like seasonal buying trends and long-term differences between metros can look like hurricane effects unless you control for them properly.

---

## Hypotheses for Milestone 3

### **Hypothesis 1: Hurricane Exposure Reduces Short-Term Housing Demand (Transaction Volume)**
- **Claim:** More exposed metros have lower Sales_Count, longer Days_on_Market, and weaker Market_Temp in the 0-6 months after major storms.
- **Model Specification:** Panel fixed-effects model with hurricane exposure and short lags; controls for seasonality, Metro FE, Time FE, and lagged inventory.
- **Expected Sign:** Higher hurricane exposure -> lower Sales_Count and weaker market heat; longer Days_on_Market.
- **Mechanism:** Buyers delay purchases, some sellers pause listings, and market activity slows.

### **Hypothesis 2: Rent-Price Linkage as a Fundamentals Check (ZORI-ZHVI)**
- **Claim:** Rent to price behavior helps detect where prices are supported by fundamentals versus potential overvaluation.
- **Model Specification:** Regression of ZORI (or rent growth) on ZHVI growth, hurricane exposure, and affordability/income controls.
- **Expected Sign:** Positive link between rent and price growth on average; large positive price residuals with weaker rent support may indicate overheating.
- **Mechanism:** If rents do not move with prices, valuation may be driven more by expectations than fundamentals.

### **Hypothesis 3: Effects Are Larger in Small, High-Exposure Metros**
- **Claim:** Small, highly exposed metros experience stronger negative storm effects than large, less exposed metros.
- **Model Specification:** Interaction rich DiD/event study (Exposure x Post x Size).
- **Expected Sign:** Negative interaction on demand/stability outcomes in small high-exposure markets.
- **Mechanism:** Thin markets have less buffer inventory and fewer substitution options.

### **Hypothesis 4: Affordability Barriers Rise with Disaster Risk**
- **Claim:** Income_Needed is higher in higher exposure metros, consistent with a risk premium.
- **Model Specification:** Metro-level panel model with Income_Needed as outcome and hurricane exposure as key regressor; controls for price growth and local labor-market conditions.
- **Expected Sign:** Positive coefficient on hurricane exposure.
- **Mechanism:** Higher insurance, financing risk, and construction costs can raise required income to buy.

---

## Data Quality Flags & Mitigation Strategies

### **Flag 1: Outlier Periods**
- **Issue:** The 2008-2012 crash and extreme hurricane years can dominate model fit.
- **Planned M3 mitigation:** Include crisis controls, run pre/post-crisis subsamples, and report robustness with/without extreme years.

### **Flag 2: Missing Values**
- **Issue:** ZORI, Inventory, Days_on_Market, and Sales_Count are sparse before about 2018.
- **Planned M3 mitigation:** Use ZHVI as the broad baseline, restrict sparse-variable models to post-2017 windows, and report sample sizes for every model.

### **Flag 3: Heteroskedasticity**
- **Issue:** Variance differs across metros and over time (large metros and crisis periods show larger spread).
- **Planned M3 mitigation:** Use heteroskedasticity-robust and clustered standard errors; check residual plots as part of diagnostics.

### **Flag 4: Multicollinearity**
- **Issue:** Hurricane cost, wind, and pressure are highly correlated.
- **Planned M3 mitigation:** Use single-metric baseline specs, run PCA robustness, and report VIF values.

---

## Summary Statistics for M3 Model Specification

| Metric | Mean | Std. Dev | Min | Max | Notes |
|--------|------|----------|-----|-----|-------|
| **ZHVI ($)** | 223,400 | 106,500 | 79,200 | 616,000 | Primary outcome; very little missing data. |
| **Hurricane Total Cost ($B)** | 5.2 | 18.4 | 0.0 | 127.0 | Right-skewed; bins may help. |
| **Hurricane Count** | 0.22 | 0.44 | 0.0 | 3.0 | Zero-inflated monthly distribution. |
| **Sales Count** | 4,200 | 5,100 | 50 | 28,000 | Sparse pre-2018 coverage; use cautiously. |
| **Market Temp** | 35.5 | 24.1 | -50 | 90 | Interpretable but incomplete in early years. |

---

## Planned M3 Model and Mitigations

1. We’ll model housing prices using hurricane exposure, while controlling for differences across cities and time. 
- Control for each metro (fixed differences between cities)
- Control for time (shared economic trends each month)
- Include seasonality only if it’s not already covered by time fixed effects
- Use clustered errors for more reliable results
(If we include year-month fixed effects, we don’t need separate seasonal controls, just pick one and stay consistent.)
2. Extra Tests
- Add short time lags for hurricane effects
- Test if effects differ by market size (small vs big cities)
- Run event-study / DiD around major hurricanes
- Try other outcomes (sales, days on market, etc.)
3. Data Issues/Fixes
- Hurricane variables overlap: keep it simple (one main measure), check robustness
- Spatial overlap: cluster errors + test spatial effects
- Missing data: limit time periods and be clear about it
- 2008 crash effects: control for it and test before/after
4. Next Steps
- Run the main model + event study
- Check results across different groups (time periods, city size, exposure levels)
- Report results in simple terms (like % changes)
- Include data checks + limitations in the appendix

