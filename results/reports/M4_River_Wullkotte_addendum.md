# Individual Addendum - River Wullkotte

## Personal Contribution

- Wrote the data quality reports for M1, M2, and M3—basically going through each dataset, checking what was missing or weird, and making sure all our variables were constructed right (3 hours)
- Did QA on the regression outputs, diagnostics, and forecast models to make sure everything actually made sense and was reproducible. Caught a few things that didn't line up the first time around (3 hours)
- Put together the M3 interpretation memo so the results were clear and easy to follow—walked through the main finding, explained what might be driving it, and compared the different models (3 hours)
- Coordinated the documentation across all three milestones and cleaned up tables and formatting for the final presentation (3 hours)

## One Defended Decision

I pushed for using clustered standard errors at the metro level in our regression models, and I'm glad we did. When I was checking the results, I realized that metros have observations stacked over time, so the errors within each metro are correlated. If you ignore that and just use regular OLS, you end up with standard errors that are way too small, and you think your results are significant when they're not. In our case, the main interaction term's p-value went from looking really solid to just barely significant (p = 0.0120) once we accounted for clustering. It made a real difference in how confident we should be, and it's the right way to handle panel data where you have multiple metros.

## One Key Limitation

The biggest issue is that not all Florida metros get hit equally by hurricanes. Coastal metros obviously get way more storm exposure than inland ones, so our effect might be picking up differences between coastal and inland markets rather than a pure storm effect. It's hard to tell where the storm impact ends and just "being a coastal market" begins. This means we should be careful about applying our results to other parts of Florida or other regions, especially if they have different geography or storm patterns.

## AI Audit Notes

Everything should be in the team appendix.