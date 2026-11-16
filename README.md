# MTA-access — longitudinal subway elevator service continuity

This repository contains a CPU-only, reproducible analysis of public Metropolitan Transportation Authority (MTA) elevator reliability data.

## Target paper

Primary target: **Journal of Transport Geography**

Working title:

**Reliability or continuity? How measurement changes the geography of New York subway elevator service**

The paper has one primary message: **the denominator used to measure operational reliability can change the spatial diagnosis of persistent service disadvantage when denominator-excluded time is geographically concentrated.**

The project deliberately does not claim novelty for passenger OD impacts of elevator failures. Existing public work already combines elevator vertical-path redundancy with passenger flows. The present study addresses a different longitudinal measurement question.

## Research questions

1. How large and spatially variable is the gap between MTA-reported in-service elevator availability and calendar service continuity?
2. Does denominator choice change which station complexes are identified as chronically low-reliability places?
3. Are relative station-complex reliability rankings persistent across years?
4. Do asset-level and official accessible-platform indicators yield the same spatial ordering?
5. As a secondary explanatory analysis, is maintenance governance associated with reported asset availability after temporal and station-complex controls?

## Data

Official sources:

- MTA NYCT Subway Elevator and Escalator Availability: Beginning 2015  
  https://data.ny.gov/d/rc78-7x78
- MTA Subway Accessible Station Platform Availability: Beginning 2018  
  https://data.ny.gov/d/thh2-syn7
- MTA Subway Stations and Complexes  
  https://data.ny.gov/d/5f5g-n3cz
- NYC Department of City Planning Borough Boundaries  
  https://data.cityofnewyork.us/d/gthc-hcne

The frozen submission analysis uses the 2026-11-16 snapshots. The panel contains:

- **46,400 elevator-month observations**
- **420 elevator assets**
- **133 station complexes**
- January 2015 through October 2026
- zero duplicate equipment-month keys

The repository also supports a manual workflow that downloads the latest official releases for prospective reproduction. The latest-data verification run on 2026-11-16 produced the same SHA-256 hashes as the frozen primary MTA snapshots, so the manuscript results did not require updating.

## Measurement framework

MTA-reported in-service availability:

`A = hours available / MTA-reported denominator hours`

Calendar service continuity:

`C = hours available / calendar hours in the asset-month`

Calendar continuity is a complementary asset-service measure. It is **not** labelled “true availability” and is **not** interpreted as a passenger-level probability of completing a step-free journey.

NYC accessibility reporting notes that elevator availability excludes elevators out for planned replacements. The analysis asks whether retaining denominator-excluded calendar time changes the geography of longitudinal service monitoring.

## Principal verified results

- 2025 reported systemwide elevator availability: **97.61%**
- 2025 calendar service continuity: **90.20%**
- difference: **7.41 percentage points**
- 2025 Bronx gap: **15.77 percentage points**
- mean adjacent-year Spearman correlation of station-complex reported-availability rankings: **0.562**
- third-party coefficient with month and station-complex fixed effects: **−4.99 pp** (secondary associational result)
- asset-level vs official accessible-platform availability: Spearman rho **0.697**
- exact four-borough ranking agreement: **11/105 months (10.5%)**

Management results are observational and are not interpreted causally.

## Reproducibility

Install dependencies and run the analysis locally:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v

python src/longitudinal_analysis.py \
  --main <elevator_availability.csv> \
  --platform <platform_availability.csv> \
  --output outputs/real_analysis
```

Figure generation is separated from numerical analysis and exports 300 dpi PNG files.

## GitHub Actions policy

The workflow `.github/workflows/reproduce-jtg.yml` is **manual-only** (`workflow_dispatch`). Ordinary code and manuscript commits do not trigger computation.

The workflow is used only after local validation to:

1. select the frozen data or download the latest official MTA releases;
2. run syntax checks and unit tests;
3. reproduce the numerical analysis;
4. regenerate the 300 dpi figures;
5. verify DPI metadata and record input hashes;
6. upload a reproducibility artifact.

A complete latest-data run succeeded on 2026-11-16. Earlier development failures are retained in the GitHub Actions history for transparency; they were used to identify workflow/runtime issues before the final successful run.

## Manuscript

The `manuscript/` directory contains the JTG-oriented Elsevier LaTeX workspace:

- `manuscript_blind.tex` — double-anonymized manuscript
- section source files
- `references.bib`
- `highlights.txt`
- `title_page_template.tex`
- `build_submission.py` — prepares a flat Editorial Manager source directory

The manuscript uses Elsevier `elsarticle` with author-year references. The title page remains separate from the anonymous manuscript for double-anonymized review.
