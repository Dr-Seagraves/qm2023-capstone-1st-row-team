# Individual Addendum - Nevaeh Marquez

Name: Nevaeh Marquez
Team: 1st Row Team
Date: May 1, 2026

1. Personal Contribution
- Cleaned and merged Zillow and NOAA source files into the analysis-ready metro panel; checked missingness and monthly alignment across variables (4 hours).
- Reviewed final summary statistics and source documentation so the M3 and M4 writeups used consistent variable definitions (2 hours).

2. One Defended Decision
I recommended using ZHVI as the main outcome because it has the most complete metro-level coverage and consistent monthly alignment. This choice preserved sample size for the primary fixed-effects estimation while allowing comparison across metros without losing many observations to sparse indicators.

3. One Key Limitation
Some detailed market measures (sales count, days on market, inventory) are incomplete early in the sample, which forces some analyses to use shorter windows. This limitation reduces confidence for claims about those specific metrics across the full period; the strongest results are therefore for price growth (ZHVI).

4. AI Audit Notes
Prompt: “Help me phrase the data-cleaning and merge steps for a capstone addendum in plain language.”
Output: AI suggested concise wording describing merges and missingness checks.
Verification: I compared the suggested wording against the actual pipeline code and outputs and edited to match reality.
