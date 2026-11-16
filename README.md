# MTA Accessibility Reliability — reproducible research pilot

This repository audits public MTA monthly elevator availability records before any station-level accessibility or equity claims are made.

## Research question
Do asset-level reliability summaries conceal persistent variation across stations? Which conclusions are supportable from monthly device data, and which require additional station connectivity or passenger-flow information?

## Official source
- [Monthly elevator and escalator availability (2015 onward)](https://data.ny.gov/d/rc78-7x78)
- [MTA accessible platform availability](https://data.ny.gov/d/thh2-syn7)

## Reproduce locally (CPU; no GitHub Actions)
```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.audit --input data/synthetic_fixture.csv --output outputs
```

To audit official records, download the CSV from https://data.ny.gov/api/views/rc78-7x78/rows.csv?accessType=DOWNLOAD to `data/raw.csv`, then run:

```bash
python -m src.audit --input data/raw.csv --output outputs
```

## Scientific safeguards
- A monthly device availability percentage is **not** station-level accessible journey uptime.
- Never multiply marginal device uptimes into path uptime without outage co-occurrence and station connectivity evidence.
- `station_month_diagnostic.csv` is **diagnostic only**, not measured passenger accessibility.
- Population, ridership and service-equity conclusions require separate verified data and defensible joins.
- Analysis of real MTA data has **not yet** been completed.
- No GitHub Actions workflow is included. Tests run locally to avoid consuming workflow minutes.
