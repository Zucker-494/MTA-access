# JTG submission checklist

Status legend: [x] complete; [ ] requires final author input or a submission-stage decision.

## Scientific manuscript
- [x] Primary message fixed: denominator choice -> spatial reclassification -> persistence.
- [x] Frozen analysis uses 46,400 elevator-month observations, 420 elevators and 133 complexes.
- [x] Chronicity missingness corrected: undefined MTA-reported months remain missing.
- [x] South Ferry/Whitehall recurrence corrected to 12.4% -> 29.6%.
- [x] Coverage sensitivity corrected to rho = 0.863–0.877.
- [x] Low-threshold sensitivity added.
- [x] Calendar-continuity rank persistence added.
- [x] Partial-2026 sensitivity added.
- [x] 2015–2025 common-asset sensitivity added.
- [x] Bronx excluded-time concentration quantified.
- [x] Cross-scale analysis renamed and treated as comparison/concordance rather than validation.
- [x] Maintenance-governance analysis moved to Supplementary Material.
- [x] Main-text accessibility language restricted to the service-side infrastructure level.
- [x] Data-availability and generative-AI declarations retained.

## Figures and tables
- [x] Five main figures supplied separately as 300 dpi PNG.
- [x] Two supplementary figures supplied separately as 300 dpi PNG.
- [x] Figure 1 map uses mutually exclusive symbols, external legend, north arrow and 5 km scale bar.
- [x] Figure 1 cites MTA station coordinates and NYC DCP borough boundaries.
- [x] Figure 3 redesigned as ordered bars to remove scatter/label overlap.
- [x] Figure 5 redesigned as monthly rank-concordance series to remove borough-month overplotting.
- [x] Supplementary Figure S1 uses separated coefficient intervals.
- [x] Supplementary Figure S2 uses one calendar-persistence series.
- [x] Main tables remain editable LaTeX.

## Reproducibility
- [x] Main code syntax and unit tests pass in GitHub Actions.
- [x] Corrected-result assertions pass.
- [x] Official MTA station-coordinate snapshot regenerated directly from dataset 5f5g-n3cz.
- [x] Frozen input hashes are stored under `results/input_sha256.txt`.
- [x] Normal reproduction workflow is manual-only.

## Title page — final author input required
- [ ] Confirm final author list and author order.
- [ ] Fill corresponding-author email.
- [ ] Confirm additional affiliations if applicable.
- [ ] Confirm acknowledgements.
- [ ] Confirm funding statement.
- [ ] Confirm declaration of competing interests.
- [ ] Confirm CRediT roles for every final author.

## Submission declarations
- [ ] Confirm manuscript is not under consideration elsewhere.
- [ ] Confirm all final authors approve submission.
- [ ] Decide repository visibility and archival DOI/URL.
- [ ] Choose subscription or open-access publication route.

## Optional
- [ ] Graphical abstract.
- [ ] Suggested reviewers if requested by Editorial Manager.
