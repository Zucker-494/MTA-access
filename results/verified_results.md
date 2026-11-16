# Verified results — 2026-11-16 data snapshot

## Core result
The uploaded MTA asset-month data reproduce the published availability percentage exactly from available hours divided by the reported denominator hours. The analysis then computes a separate **calendar service continuity** sensitivity measure using calendar hours as the denominator.

In 2025:
- systemwide reported in-service availability = **97.61%**
- systemwide calendar service continuity = **90.20%**
- gap = **7.41 percentage points**
- NYCT-managed reported availability = **98.17%**
- NYCT-managed calendar service continuity = **89.62%**
- NYCT-managed gap = **8.55 percentage points**

NYC's 2025 AccessibleNYC report explicitly notes that elevator availability rates exclude elevators out for planned replacements:
https://www.nyc.gov/site/mopd/publications/accessiblenyc-2025-report-transportation.page

This is a measurement distinction, not a claim that the agency KPI is arithmetically incorrect.

## Longitudinal spatial persistence
The station-complex ranking of reported availability is positively persistent in every adjacent-year comparison from 2015–2016 through 2025–2026. Mean adjacent-year Spearman rho = **0.562**. The represented accessible-elevator network expands from 86 station complexes in 2015 to 133 in 2026.

## Management governance
Cluster-robust OLS:
- month + borough FE: third-party coefficient **-4.43 pp**, p=0.000534
- month + station-complex FE: **-4.99 pp**, p=0.00547
- mixed-management complexes only: **-4.92 pp**, p=0.00628

These are observational associations and should not be described as causal effects.

## Cross-scale metric validation
For 420 borough-month observations in the overlapping 2018–2026 period:
- Pearson r = **0.671**
- Spearman rho = **0.697**
- MAE = **1.23 pp**
- asset-minus-platform mean bias = **+0.76 pp**
- complete four-borough ranking agreement = **11/105 months (10.5%)**
- 64.5% of borough-month rank positions differ

The two metrics operate at different aggregation levels. The finding is that metric choice changes spatial diagnosis, not that either metric is invalid.

## Research boundary
A recent 2026 public NYC step-free-network project already links vertical elevator redundancy with OD passenger flow. This project therefore does not claim novelty for outage-to-OD accessibility modeling. Its distinct contribution is the longitudinal measurement/gap analysis, spatial persistence, and maintenance-governance comparison.
