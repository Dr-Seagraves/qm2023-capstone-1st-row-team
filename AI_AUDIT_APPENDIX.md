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

## Summary

Total AI use: AI tools (GitHub Copilot, Claude Opus 4.6) were used for 5 tasks during pipeline development.

Primary use cases: Data import code generation, dashboard creation (later removed in favor of a single-script pipeline), documentation drafting, data dictionary generation, and data quality report structure.

Verification method: All AI-generated code was manually reviewed, tested by running the pipeline end-to-end, and outputs confirmed with instructor feedback.

Responsibility: All code is tested and our responsibility.
