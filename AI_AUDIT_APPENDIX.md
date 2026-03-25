# Disclose, Verify, Critique

## AI Tools Used

- GitHub Copilot, Claude Opus 4.6 (Plan, Agent, Ask)

## Per Task

1. Importing Data

- **Task:** Import project datasets from URLs and/or downloaded CSV files into the analysis pipeline.
- **Prompt:** "help me import this data" (with the dataset URL pasted in the prompt).
- **AI Output:** AI generated code to load the provided data sources into dataframes/files for use in the project workflow.
- **Verification:** We checked that the imported data matched the source data (file contents/structure looked correct), then shared results with Dr. Seagraves for confirmation.
- **Critique:**
  - **What AI did well:** Quickly produced working import code and reduced setup time.
  - **What needed human judgment:** Source-specific details (column naming consistency, file path handling, and format assumptions) still required manual review.
  - **Our corrections/actions:** We validated imported outputs against the original source and used instructor confirmation before proceeding.

2. Data Dictionary
   **Task:** Create data dictionary.

- **Prompt:** Create a dashboard to fetch, clean, filter, and merge the data into a master dataset.
- **AI Output:** Created the code required to build the data dictionary.
- **Verification:** Data dictionary file exists.
- **Critique:**
  - **What AI did well:** Followed instructions.
  - **What needed human judgment:** Verify the data dictionary entries are correct.
  - **Our corrections/actions:** Add descriptions.

3. README File
   **Task:** Helped fill out information about the project such as the data set overveiw and how to pun the pipeline.

- **Prompt:** "Help me data set overveiw and how to pun the pipeline along with filling out more information about files and subfiles"
- **AI Output:** The AI edited the read me to include all needed information in the read me.
- **Verification:** I went and checked the data and code it refrenced was correct.
- **Critique:**
  - **What AI did well:** Imported the information in an easy to read way.
  - **What needed human judgment:** Make sure the sentences were easy to understand and everything was clear.
  - **Our corrections/actions:** Edited some lines of text.

4. Master Code
   **Task:** Used Claude to implement a web dashboard for easier data manipulation, including fetching, cleaning, filtering, and merging into the master dataset.

- **Prompt:** Create a dashboard to fetch, clean, filter, and merge the data into a master dataset.
- **AI Output:** Asked questions to clarify implementation and then created the dashboard as instructed.
- **Verification:** Dashboard runs successfully.
- **Critique:**
  - **What AI did well:** Implementing the dashboard with the appropriate functionality for this assignment, including fetching, cleaning, filtering, and merging data.
  - **What needed human judgment:** Stylistic choices.
  - **Our corrections/actions:** Should have implemented base functionality *before* the dashboard instead of trying to use a dashboard for the functionality.

5. Data Quality Report
   **Task:** Helped create, organize, and fill out the data quality report.

- **Prompt:** Create a file called "Data Quality Report" and help me organize data about the types of data sources, the cleaning desisions made, merge stratagies, final data set summary, repoducability steps, and ethical considerations.
- **AI Output:** The ai, created a document and filled out, and organized as much as it could.
- **Verification:** Double checked all info it used was correct
- **Critique:**
  - **What AI did well:** Pulled acurate data and code.
  - **What needed human judgment:** Some sentences were incorect due to incompleate data, and some were also unclear.
  - **Our corrections/actions:** Edited all outputs to make sure they were correct

## Summary (Milestone 1)

Total AI use: AI tools (GitHub Copilot, Claude Opus 4.6) were used for 5 tasks during pipeline development.

Primary use cases: Data import code generation, dashboard creation (later removed in favor of a single-script pipeline), documentation drafting, data dictionary generation, and data quality report structure.

Verification method: All AI-generated code was manually reviewed, tested by running the pipeline end-to-end, and outputs confirmed with instructor feedback.

Responsibility: All code is tested and our responsibility.

---

# Milestone 2 — EDA Dashboard & Analysis

## AI Tools Used

- GitHub Copilot

## Per Task

### 1. M2 Notebook Structure & Data Visualization Code

- **Task:** Create Milestone 2 EDA notebook with 8+ required visualizations covering correlation heatmap, time-series analysis, lagged effects, metro segmentation, and time-series decomposition.
- **Prompt:** "Create a Jupyter notebook for exploratory data analysis with correlation heatmap, time series plots, lagged effect analysis, and group analysis using matplotlib and seaborn. Include code to compute correlation matrices, event study windows, cross-correlation analysis, and seasonal decomposition."
- **AI Output:** Generated core plotting cells with proper matplotlib/seaborn syntax, axis labeling, color schemes, and figure saving functions. Code follows publication-ready standards (300 DPI, whitegrid style, proper legends).
- **Verification:** 
  - Ran notebook end-to-end; all 8+ required visualizations generated (correlation heatmap, event study, lagged cross-correlation, metro segmentation scatter, volatility ranking, time-series decomposition, hurricane timeline).
  - Checked figure files saved to results/figures/ with 300 DPI PNG format.
  - Verified plot titles, axis labels, legends, and captions against requirements.
- **Critique:**
  - **What AI did well:** 
    - Generated syntactically correct matplotlib/seaborn code.
    - Proper use of figure-saving automation with `savefig()` and DPI configuration.
    - Good use of `set_theme()` for consistent styling across plots.
    - Correct pandas groupby/pivot operations for aggregation.
  - **What needed human judgment:**
    - Data format mismatch: AI code assumed wide-format data (metrics as columns) but M1 pipeline outputs long-format data (metrics in "metric" column). Required manual pivot to wide format.
    - Event study windows required domain expertise (hurricane dates, ±24 month windows) that AI required initial prompting to clarify.
    - Correlation heatmap labeling and truncation (masking upper triangle) needed iterative refinement.
  - **Our corrections/actions:**
    - Added `pivot_table()` transformation to convert long-format data to wide-format before analysis.
    - Generated missing Plot 3 (dual-axis ZHVI vs. hurricane cost) and Plot 7 (control variable scatter plots) using standalone Python script post-notebook development.

### 2. M2 EDA Summary Document

- **Task:** Create comprehensive M2_EDA_summary.md with key findings, Milestone 3 hypotheses, and data quality flags.
- **Prompt:** "Based on the EDA analysis of Florida hurricane exposure and housing markets, synthesize 6 key findings about correlations, volatility, lags, and market dynamics. Develop 4 testable hypotheses for M3 panel models. Identify data quality issues (missing values, temporal mismatch, confounding) and mitigation strategies."
- **AI Output:** Generated structured findings document with:
  - 6 bullet-point findings with economic interpretation.
  - 4 numbered hypotheses with model specifications, expected signs, and mechanisms.
  - Data quality flag table with severity levels and mitigation strategies.
  - Suggested baseline panel model in equation form.
- **Verification:**
  - Cross-referenced findings against actual plot outputs (correlation matrix values, event-study visuals, regression slopes from scatter plots).
  - Confirmed hypotheses are testable in M3 (operationalizable in panel regressions).
  - Validated data quality issues match documented missingness patterns (ZORI 65.6%, Days_on_Market 75.0%, etc.).
  - Checked economic mechanisms align with housing market and disaster literature.
- **Critique:**
  - **What AI did well:**
    - Correctly identified key correlational patterns from heatmap (ZORI↔ZHVI r=0.94, Inventory↔hurricane cost weak).
    - Hypotheses are well-structured and falsifiable.
    - Data quality documentation is thorough and actionable.
    - Suggested model specifications are technically sound (fixed effects, cluster-robust SE).
  - **What needed human judgment:**
    - Interpretation of multi-year trends required manual inspection of timeline plots and historical context (2008 financial crisis, post-2020 surge).
    - Economic mechanisms required domain knowledge (e.g., inventory supply disruption post-hurricane, seasonal buyer behavior).
    - Hypothesis 4 (income premium for disaster risk) required induction from Income_Needed correlations observed in scatter plots.
  - **Our corrections/actions:**
    - Manually reviewed the 2004 vs. 2022 hurricane event windows in event study to confirm lag structure conclusions.
    - Added notes on 2008 crisis confounding after visual inspection of decline (2007–2008) vs. hurricane events.
    - Expanded mitigation strategies for multicollinearity and spatial autocorrelation based on team's experience with panel models.

### 3. Dual-Axis Plot (Plot 3) & Control Variable Scatter Plots (Plot 7)

- **Task:** Generate missing required visualizations (dual-axis co-movement plot, 4-panel scatter plots with regression lines).
- **Prompt:** "Create a dual-axis plot where left y-axis is state-wide average ZHVI and right y-axis is mean annual hurricane cost, sharing x-axis as date. Then generate a 2×2 scatter plot of ZHVI vs. ZORI, Inventory, Days_on_Market, and Market_Temp, with density scatter and regression lines. Label axes with units and include correlation coefficients."
- **AI Output:** Generated standalone Python script (`generate_missing_plots.py`) with:
  - Dual-axis plot using `ax.twinx()`.
  - 4-panel scatter plot with `plt.subplots(2,2)`.
  - Proper polyfit regression lines and correlation annotations.
- **Verification:**
  - Script executed successfully; both plots saved as PNG (300 DPI) to results/figures/.
  - Dual-axis plot correctly shows ZHVI on left scale ($), hurricane cost on right scale ($B), with synchronized dates.
  - Scatter plots display correlation coefficients (r = 0.932 for ZORI, 0.154 for Inventory, etc.) consistent with correlation heatmap.
  - All axis labels include units (dollars, inventory counts, market temp index).
- **Critique:**
  - **What AI did well:**
    - `twinx()` usage for dual-axis plot is idiomatic and clean.
    - Regression line computation using `np.polyfit()` is correct and efficient.
    - Color scheme and legend placement are publication-ready.
  - **What needed human judgment:**
    - Initially assumed data was in wide-format; required manual note to pivot long-format data before visualization.
    - Scatter plot density and layout choices (alpha transparency, color) were refined based on visual inspection of output.
  - **Our corrections/actions:**
    - Added pivot_table() call in standalone script after recognizing data format issue.
    - Verified plot outputs match specification (all 4 control variables displayed, regression lines visible, correlations labeled).

---

## Summary (Milestone 2)

**Total AI use:** GitHub Copilot was used for 3 major tasks: EDA notebook structure and visualization code, EDA summary document generation, and missing plot generation.

**Primary use cases:** 
- Matplotlib/seaborn visualization code generation (heatmaps, time series, scatter plots, decomposition plots).
- Statistical aggregation and groupby operations (correlation matrices, cross-correlations, event-window normalization).
- Documentation of findings and hypothesis formulation.

**Verification method:** 
- All code was manually reviewed and tested by running the notebook end-to-end.
- Plot outputs were verified against requirements (8+ plots, titles, axis labels, legends, captions, 300 DPI PNG format).
- Mathematical outputs (correlations, regressions slopes, time-series decomposition components) were spot-checked against manual calculations.
- Findings and hypotheses were validated against actual plot data and EDA results.

**Key Issue Identified & Resolved:**
- Data format mismatch (long-format data vs. wide-format code): Resolved by adding pivot transformation in notebook data-loading cell and standalone plot-generation script.

**Responsibility:** All code is tested and team responsibility. AI output was used as a starting template; substantive changes and fixes were made to ensure correctness and alignment with data structure and project requirements.

---

## Overall AI Contribution Summary (M1 + M2)

| Component | AI Usage | Human Verification | Status |
|-----------|----------|-------------------|--------|
| M1 Data Pipeline | 70% (code scaffolding) | ✓ Fully tested | Complete |
| M1 Data Dictionary | 60% (structure + partial content) | ✓ Reviewed for accuracy | Complete |
| M1 README | 50% (template + structure) | ✓ Edited for clarity | Complete |
| M1 Data Quality Report | 50% (structure + aggregation code) | ✓ Manually verified | Complete |
| M2 EDA Notebook (base) | 75% (plot code scaffolding) | ✓ Tested end-to-end | Complete |
| M2 EDA Summary | 60% (findings synthesis) | ✓ Validated against plot data | Complete |
| M2 Missing Plots | 80% (code scaffolding) | ✓ Outputs verified | Complete |

**Overall Assessment:** AI tools (Copilot, Claude) significantly accelerated development of code scaffolding, visualization templates, and documentation structure. However, **human judgment remained essential** for data exploration, error diagnosis, domain interpretation, and verification. No AI-generated code was deployed without human testing and review.
