# New York subway elevator service continuity

This repository contains the data and analysis files used to examine how the temporal denominator of an elevator-service indicator affects spatial diagnosis across the New York City subway.

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
- **Calendar service continuity**: hours available divided by the full calendar hours of each observed equipment-month.

The comparison is used to examine whether denominator choice changes the numerical level of service indicators and the spatial identification of persistently low-performing station complexes.

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

Run the longitudinal analysis with the frozen MTA files:

```bash
python src/longitudinal_analysis.py \
  --main data/MTA_NYCT_Subway_Elevator_and_Escalator_Availability__Beginning_2015_20261116.csv \
  --platform data/MTA_Subway_Accessible_Station_Platform_Availability__Beginning_2018_20261116.csv \
  --output results
```

Station-complex coordinates can be prepared from the official station dataset with `src/prepare_station_coordinates.py`. Figure-generation code is provided in `src/make_figures.py`.

## Data provenance

All source datasets are public. The copies in `data/` are retained to preserve the exact data state used in the analysis.
