# Individual Addendum - River Wullkotte

Name: River Wullkotte
Team: 1st Row Team
Date: May 1, 2026

1. Personal Contribution
- Wrote data quality reports for M1–M3 and performed QA on regression outputs, diagnostics, and forecast models (3 hours).
- Prepared the M3 interpretation memo and coordinated documentation across milestones (3 hours).
- Cleaned and formatted tables and figures for final submission (3 hours).

2. One Defended Decision
I pushed to use clustered standard errors at the metro level for FE models. Panel observations by metro induce within-metro correlation in errors; clustering increases standard errors appropriately and avoids overstating significance. In our case, the main interaction term’s SE widened materially under clustering, which changed interpretation and was the correct conservative approach.

3. One Key Limitation
Not all metros face equal storm risk; coastal metros see more exposure than inland ones. Our state-level cost proxy and metro interactions may partly reflect coastal/inland differences rather than purely storm-driven effects. This threatens external validity and motivates further metro-specific exposure measurement.

4. AI Audit Notes
Prompt: “Help me draft concise M3 and M4 memo language that matches the statistics in our regression tables.”
Output: AI produced a first-pass explanation for the clustered FE result and the scenario language.
Verification: I cross-checked wording against `results/tables/M3_regression_table.csv` and `M3_robustness_checks.csv`, and edited to avoid causal overreach.