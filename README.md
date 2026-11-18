# New York subway elevator service continuity

This repository contains the frozen data and analysis files used to examine how the temporal denominator of an elevator-service indicator affects transport infrastructure monitoring across the New York City subway.

## Data

The analysis uses public data from the Metropolitan Transportation Authority (MTA) and New York City Department of City Planning:

- MTA NYCT Subway Elevator and Escalator Availability: Beginning 2015  
  https://data.ny.gov/d/rc78-7x78
- MTA Subway Accessible Station Platform Availability: Beginning 2018  
  https://data.ny.gov/d/thh2-syn7
- MTA Subway Stations and Complexes  
  https://data.ny.gov/d/5f5g-n3cz
- NYC Department of City Planning Borough Boundaries  
  https://data.cityofnewyork.us/d/gthc-hcne

The frozen analysis uses data downloaded on 16 November 2026 and covers January 2015 through October 2026.

## Measures

Two equipment-level measures are compared:

- **MTA-reported availability**: hours available divided by the denominator hours reported by the MTA.
- **Calendar continuity**: hours available divided by the full calendar hours of each observed equipment-month.

For observations with a positive reported denominator, calendar continuity equals conditional availability multiplied by reported-hour coverage.

## Repository structure

- `data/` — frozen source data and station-complex coordinates
- `src/` — analysis and figure-generation scripts
- `results/` — derived tables used in the analysis
- `requirements.txt` — Python package requirements

## Reproduction

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

Run the longitudinal preprocessing and descriptive analysis:

```bash
python src/longitudinal_analysis.py \
  --main data/MTA_NYCT_Subway_Elevator_and_Escalator_Availability__Beginning_2015_20261116.csv \
  --platform data/MTA_Subway_Accessible_Station_Platform_Availability__Beginning_2018_20261116.csv \
  --output results
```

The TR-A manuscript uses **common-support fixed-capacity screening**. Run:

```bash
python src/common_support_analysis.py \
  --complex-month results/complex_month.csv \
  --output results
```

For each month, the common-support set contains station complexes for which both MTA-reported availability and calendar continuity are defined. For screening share `q`, the target count is `floor(q * N_common)`; the same count is applied to both indicator rankings. Station-complex ID is the deterministic secondary ordering for exact metric ties.

The script writes:

- `results/common_support_screening_summary.csv`
- `results/common_support_recurrence_quartile.csv`

Station-complex coordinates can be prepared from the official station dataset with `src/prepare_station_coordinates.py`.

## Data provenance

All source datasets are public. The copies in `data/` are retained to preserve the exact data state used in the analysis.
