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

- GitHub Copilot, Claude Opus 4.6

## Per Task

### 1. M2 Notebook Structure & Data Visualization Code

- **Task:** Create Milestone 2 EDA notebook with 8+ required visualizations covering correlation heatmap, time-series analysis, lagged effects, metro segmentation, and time-series decomposition.
- **Prompt:** "Create a Jupyter notebook for exploratory data analysis with correlation heatmap, time series plots, lagged effect analysis, and group analysis using matplotlib and seaborn. Include code to compute correlation matrices, event study windows, cross-correlation analysis, and seasonal decomposition."
- **AI Output:** AI generated base notebook cells for plots and summary statistics.
- **Verification:** We ran the notebook end-to-end and checked each required plot.
- **Critique:**
  - **What AI did well:** It gave fast plotting code and useful templates.
  - **What needed human judgment:** We adjusted plot choices, labels, and interpretation.
  - **Our corrections/actions:** We fixed data shape issues and refined plots to meet the rubric.

### 2. M2 EDA Summary Document

- **Task:** Create comprehensive M2_EDA_summary.md with key findings, Milestone 3 hypotheses, and data quality flags.
- **Prompt:** "Based on the EDA analysis of Florida hurricane exposure and housing markets, synthesize 6 key findings about correlations, volatility, lags, and market dynamics. Develop 4 testable hypotheses for M3 panel models. Identify data quality issues (missing values, temporal mismatch, confounding) and mitigation strategies."
- **AI Output:** AI drafted a summary with findings, hypotheses, and data quality notes.
- **Verification:** We matched each claim to notebook outputs and corrected any overstatements.
- **Critique:**
  - **What AI did well:** It gave a clear first draft fast.
  - **What needed human judgment:** Team interpretation was needed for context and limits.
  - **Our corrections/actions:** We edited wording, added caveats, and aligned claims with plots.

### 3. Dual-Axis Plot (Plot 3) & Control Variable Scatter Plots (Plot 7)

- **Task:** Generate missing required visualizations (dual-axis co-movement plot, 4-panel scatter plots with regression lines).
- **Prompt:** "Create a dual-axis plot where left y-axis is state-wide average ZHVI and right y-axis is mean annual hurricane cost, sharing x-axis as date. Then generate a 2×2 scatter plot of ZHVI vs. ZORI, Inventory, Days_on_Market, and Market_Temp, with density scatter and regression lines. Label axes with units and include correlation coefficients."
- **AI Output:** AI generated script scaffolding for the missing figures.
- **Verification:** We ran the script and confirmed saved outputs and labels.
- **Critique:**
  - **What AI did well:** It produced usable plotting blocks quickly.
  - **What needed human judgment:** We had to adapt the code to our long-format data.
  - **Our corrections/actions:** We added data reshaping and tuned styling choices.

---

## Summary (Milestone 2)

**Total AI use:** AI tools were used in notebook coding, figure generation, and summary drafting.

**Primary use cases:** plotting templates, data transform suggestions, and writing support.

**Verification method:** The team ran notebook cells, checked figures, and reviewed statements against actual results.

**Key issue identified and resolved:** Data format mismatch (long vs. wide) was fixed with manual reshaping.

**Responsibility:** AI supported the work. The team wrote final edits, tested results, and owns all outputs.

---

## Overall AI Contribution Summary (M1 + M2)

| Component | AI Usage | Human Verification | Status |
|-----------|----------|-------------------|--------|
| M1 Data Pipeline | Drafting and scaffolding support | Team tested full run | Complete |
| M1 Data Dictionary | Template and wording support | Team reviewed all entries | Complete |
| M1 README | Structure and draft text support | Team edited for accuracy | Complete |
| M1 Data Quality Report | Organization and draft support | Team verified values | Complete |
| M2 EDA Notebook | Plot and code template support | Team ran and validated outputs | Complete |
| M2 EDA Summary | Draft findings support | Team aligned claims to results | Complete |
| M2 Missing Plots | Script scaffolding support | Team verified files and labels | Complete |

**Overall Assessment:** AI helped us move faster. It was used as an assistant, not a replacement for team work. All members contributed to coding, checking, and writing. Final decisions and responsibility stayed with the team.
