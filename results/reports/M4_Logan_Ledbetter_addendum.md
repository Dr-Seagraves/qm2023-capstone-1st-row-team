# Individual Addendum - Logan Ledbetter

Name: Logan Ledbetter
Team: 1st Row Team
Date: May 1, 2026

1. Personal Contribution
- Built and maintained the reproducibility workflow, including the pipeline wrapper and model execution steps that generate final tables and figures used in the memo (6 hours).
- Debugged file-path, export, and output issues so the analysis can be rerun from a clean clone without manual edits (4 hours).

2. One Defended Decision
I advocated for a single reproducible workflow (one-command run) rather than separate manual steps. This ensured that the memo tables and figures come from the same cleaned dataset and identical lag structure, improving auditability and reproducibility.

3. One Key Limitation
The pipeline depends on external source files and URLs that may change. If a source updates or becomes unavailable, exact reproduction requires cached source copies. This matters because results can shift if underlying input versions differ.

4. AI Audit Notes
Prompt: “Draft a clean Python wrapper for a reproducible capstone workflow and suggest export structure for tables/figures.”
Output: AI provided a workflow skeleton and naming suggestions.
Verification: I ran the full workflow from the repository root and verified the expected files were generated, keeping only the structure that matched the project.
