# Verified results — corrected 2026-11-16 submission snapshot

## Primary measurement result

The frozen MTA asset-month data reproduce the published 24-hour availability field exactly from available hours divided by the MTA-reported denominator hours. The paper compares that conditional measure with **calendar continuity**, defined as available hours divided by all calendar hours in the asset-month.

For 2025:

- MTA-reported systemwide elevator availability = **97.61%**
- calendar continuity = **90.20%**
- difference = **7.41 percentage points**

The gap is spatially uneven: **15.77 pp in the Bronx**, 8.11 pp in Brooklyn, 5.20 pp in Manhattan, and 6.73 pp in Queens.

## Corrected station-complex chronicity

Missing MTA-reported availability is preserved as missing in the low-reliability indicator. A zero reported denominator is therefore excluded from the denominator of MTA-reported chronicity rather than treated as a non-low-reliability month.

With a 36-month minimum observation rule and a monthly bottom-quartile diagnostic:

- **7 complexes** are in the calendar-continuity low-reliability quartile in at least half of observed months.
- **3 complexes** have recurrence increases of at least 0.15 under calendar continuity.
- Cortlandt Street (328): **13.3% -> 67.3%**
- South Ferry/Whitehall Street (635): **12.4% -> 29.6%**
- Court Street/Borough Hall (620): **26.1% -> 43.0%**

The corrected chronicity Spearman correlation is **0.877**.

## Persistence

For MTA-reported availability, all eleven adjacent-year station-complex rank correlations are positive and statistically significant.

- mean Spearman rho = **0.562**
- range = **0.405–0.666**
- excluding the partial 2025–2026 pair: mean rho = **0.557**

Calendar continuity is also persistent:

- mean adjacent-year rho = **0.525**
- range = **0.369–0.667**

Under a common January–October window, the 2025–2026 correlations are **0.561** for MTA-reported availability and **0.477** for calendar continuity.

## Loss decomposition and spatial concentration

In 2025:

- 90.20% of elevator calendar time was recorded as available.
- 2.21% was unavailable inside the MTA-reported denominator.
- 7.59% was excluded from that denominator.
- excluded time accounts for **77.5% of total calendar service loss**.

In the Bronx, excluded time accounts for 88.4% of total calendar service loss. The excluded hours are highly concentrated:

- largest complex share = **63.3%**
- top three complexes = **96.9%**
- top five complexes = **99.4%**

The Bronx annual gap therefore reflects concentrated station-complex conditions rather than a uniform borough-wide state.

## Robustness

Removing the first and last observed month of each elevator changes 2025 calendar continuity from **90.20% to 90.29%**.

Across minimum longitudinal-coverage rules from 24 to 72 months:

- chronicity rho = **0.863–0.877**
- 7 persistent low-continuity complexes remain
- 3 complexes retain recurrence increases of at least 0.15

Across bottom-quintile, quartile, and tercile low-reliability definitions:

- chronicity rho = **0.814–0.906**
- Cortlandt Street, South Ferry/Whitehall Street, and Court Street/Borough Hall retain recurrence increases of at least 0.15 under all three definitions.

A common-asset panel of **260 elevators** observed for at least ten months in every year from 2015–2025 yields a **10.99 pp** measurement gap in 2025. The denominator effect therefore remains substantial under a stable asset set.

## Cross-scale comparison

For 420 borough-month observations in 2018–2026:

- Pearson r = **0.671**
- Spearman rho = **0.697**
- MAE = **1.23 pp**
- complete four-borough ordering agrees in **11/105 months (10.5%)**
- **64.5%** of borough rank positions change
- mean monthly Kendall concordance = **0.286**

The asset and accessible-platform metrics are numerically related but are not spatially interchangeable.

## Supplementary governance analysis

Maintenance governance is retained only as an exploratory supplementary analysis.

- month + complex FE, elevator-clustered SE: **−4.99 pp**, p=0.0055
- same model, complex-clustered SE: **−4.99 pp**, p=0.0066
- mixed-management complexes: **−4.92 pp**, p=0.0063

These estimates are associational and are not part of the primary paper contribution.
