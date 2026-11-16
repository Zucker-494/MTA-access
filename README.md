# MTA-access — longitudinal subway elevator reliability

This repository contains a CPU-only reproducible analysis of public MTA elevator reliability data.

## Current paper focus
**Reliability or continuity? Long-term spatial inequalities in subway elevator service under denominator exclusions and heterogeneous maintenance governance**

The project deliberately does **not** model passenger OD accessibility from marginal elevator uptime alone. A recent public NYC step-free-network project already combines vertical-path redundancy and OD flow; this repository instead focuses on a distinct longitudinal measurement problem:

1. whether station-complex reliability disadvantage persists over 2015–2026;
2. how excluding calendar time from the reported availability denominator changes longitudinal and spatial diagnosis;
3. whether third-party-managed elevators show a persistent availability gap after time and station-complex controls;
4. whether asset-level and official accessible-platform metrics produce the same spatial ordering.

## Verified data
Official MTA datasets:
- Elevator and escalator availability, beginning 2015: https://data.ny.gov/d/rc78-7x78
- Accessible station platform availability, beginning 2018: https://data.ny.gov/d/thh2-syn7

Local analysis used the 2026-11-16 downloads:
- `MTA_NYCT_Subway_Elevator_and_Escalator_Availability__Beginning_2015_20261116.csv`
- `MTA_Subway_Accessible_Station_Platform_Availability__Beginning_2018_20261116.csv`

Raw files are not committed. The analysis covers 46,400 elevator asset-month observations, 420 elevators and 133 station complexes from January 2015 through October 2026.

## Principal verified results
- 2025 systemwide reported in-service elevator availability: **97.61%**.
- 2025 calendar service continuity: **90.20%**.
- Difference: **7.41 percentage points**.
- Mean adjacent-year Spearman correlation of station-complex availability ranks: **0.562**.
- Third-party coefficient with month + station-complex fixed effects: **-4.99 pp** (clustered SE 1.80 pp; p=0.00547).
- Mixed-management-complex sensitivity coefficient: **-4.92 pp** (p=0.00628).
- Asset-level vs official accessible-platform availability: Spearman rho **0.697**.
- Exact four-borough ranking agreement: **11/105 months (10.5%)**.

These results are descriptive/associational. The third-party coefficient is not interpreted causally.

## Key measurement distinction
`reported availability = available hours / MTA-reported denominator hours`

`calendar service continuity = available hours / calendar hours in the asset-month`

The calendar measure retains periods omitted from the reported denominator. NYC's 2025 AccessibleNYC report explicitly notes that elevator availability rates do not include elevators out for planned replacements. Calendar continuity is therefore used as a **sensitivity measure of asset service continuity**, not as passenger-level step-free journey success.

## Reproduce locally
Place the two raw CSV files under `data/raw/`, then:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/longitudinal_analysis.py \
  --main data/raw/MTA_NYCT_Subway_Elevator_and_Escalator_Availability__Beginning_2015_20261116.csv \
  --platform data/raw/MTA_Subway_Accessible_Station_Platform_Availability__Beginning_2018_20261116.csv \
  --output outputs/real_analysis
```

## Repository outputs
- `results/verified_results.md`: current scientific result summary.
- `results/system_yearly.csv`: annual reported availability vs calendar continuity.
- `results/management_regression.csv`: fixed-effects management association.
- `results/rank_stability.csv`: adjacent-year spatial persistence.
- `results/platform_validation.csv`: cross-scale validation summary.
- `figures/README.md`: six final 300 dpi figure specifications.

## GitHub Actions
No workflow is configured. **GitHub Actions usage remains zero for this project.** All code is tested locally before being committed.
