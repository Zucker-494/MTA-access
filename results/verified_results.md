# Verified results — frozen 2026-11-16 submission snapshot

## Core measurement result

The MTA asset-month data reproduce the published 24-hour availability field exactly from available hours divided by the MTA-reported denominator hours. The paper compares that conditional operational metric with a second measure, **calendar service continuity**, defined as available hours divided by all calendar hours in the asset-month.

For 2025:

- reported systemwide elevator availability = **97.61%**
- calendar service continuity = **90.20%**
- difference = **7.41 percentage points**

The measurement gap is spatially uneven. In 2025 it reached **15.77 pp in the Bronx**, compared with 8.11 pp in Brooklyn, 5.20 pp in Manhattan, and 6.73 pp in Queens.

The distinction is supported by the MTA data definition, which excludes capital outages from reported total hours, and by AccessibleNYC 2025, which states that planned replacements are excluded from elevator availability reporting.

## Station-complex reclassification

Among 113 station complexes with at least 36 observed months:

- **7 complexes** fall in the calendar-continuity bottom quartile in at least half of their observed months.
- **3 complexes** have a bottom-quartile recurrence increase of at least 0.15 when calendar continuity replaces reported availability.
- Cortlandt Street (complex 328) changes from **13.3%** of observed months in the reported-availability bottom quartile to **67.3%** under calendar continuity.

This is the paper's principal spatial result: denominator choice changes the identification of persistently low-reliability places.

## Longitudinal persistence

All eleven adjacent-year station-complex rank correlations from 2015–2016 through 2025–2026 are positive and statistically significant.

- mean adjacent-year Spearman rho = **0.562**
- minimum = **0.405** (2019–2020)
- maximum = **0.666** (2024–2025)

## Calendar-loss decomposition

In 2025:

- 90.20% of elevator calendar time was recorded as available.
- 2.21% was unavailable inside the reported denominator.
- 7.59% was excluded from the reported denominator.
- excluded time therefore accounts for **77.5% of total calendar service loss**.

The excluded share of total loss varies spatially, including **88.4% in the Bronx** and **65.9% in Manhattan**.

## Robustness

Removing the first and last observed month of every elevator changes 2025 systemwide calendar continuity only from **90.20% to 90.29%** (+0.096 pp).

Varying the minimum station-complex observation requirement from 24 to 72 months gives chronicity Spearman correlations from **0.853 to 0.868**. Across all five thresholds, seven complexes remain in the calendar-continuity bottom quartile in at least half of observed months, and three retain a reclassification increase of at least 0.15.

## Maintenance governance — secondary explanatory analysis

Cluster-robust OLS results:

- month + borough fixed effects: third-party coefficient **−4.43 pp**, p=0.000534
- month + station-complex fixed effects: **−4.99 pp**, p=0.00547
- mixed-management complexes only: **−4.92 pp**, p=0.00628

The coefficient is interpreted as an observational association. Maintenance governance remains a secondary explanatory result; it is not the paper's primary contribution.

## Cross-scale validation

Across 420 borough-month observations in the overlapping 2018–2026 period:

- Pearson r = **0.671**
- Spearman rho = **0.697**
- MAE = **1.23 pp**
- asset-minus-platform mean bias = **+0.76 pp**
- complete four-borough ranking agreement = **11/105 months (10.5%)**
- **64.5%** of borough-month rank positions differ

The two metrics are related numerically but are not spatially interchangeable.

## Paper boundary

The study evaluates the geography of asset service continuity. It does not reconstruct complete passenger origin-destination journeys. The transferable contribution is the measurement framework: compare the operator's conditional reliability measure with calendar-time continuity and test whether place rankings remain stable when denominator-excluded time is retained.
