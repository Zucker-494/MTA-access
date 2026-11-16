# JTG manuscript workspace

Primary target: **Journal of Transport Geography**

Working title:

**Reliability or continuity? How measurement changes the geography of New York subway elevator service**

The primary paper message is now fixed:

**operational denominator choice -> spatial reclassification -> longitudinal persistence**

Maintenance governance has been moved to a separate exploratory Supplementary Material analysis.

## Main source files

- `manuscript_blind.tex` — double-anonymized master manuscript.
- `01_introduction_background.tex` — measurement problem and JTG positioning.
- `02_data_methods.tex` — data, corrected chronicity handling, spatial comparison, and robustness design.
- `03_results.tex` — corrected empirical results.
- `04_discussion_conclusion.tex` — service-side interpretation, transferability, limitations, and conclusions.
- `supplementary_material.tex` — governance analysis, calendar-continuity persistence, and chronicity sensitivity.
- `references.bib` — cited references and official data sources.
- `figure_captions.txt` — separate main-figure captions in manuscript order.
- `highlights.txt` — Elsevier highlights.
- `title_page_template.tex` — non-blinded title-page template; author details remain for manual completion.
- `cover_letter_template.txt` — working cover letter.
- `CRediT_template.txt` — author-contribution template.
- `submission_checklist.md` — final author-input and submission checks.

## Figures

The repository `figures/` directory contains five main-text PNGs and two supplementary PNGs at 300 dpi. The revised graphics were explicitly redesigned to avoid label and data overplotting.

## Flat working package

Run:

```bash
python manuscript/build_submission.py \
  --figures-dir figures \
  --output submission_flat
```

The resulting directory contains the manuscript sources, submission-support files, five main figures, two supplementary figures, and the supplementary LaTeX source at one directory level.

## Reproducibility

The corrected numerical pipeline preserves missing MTA-reported availability rather than coding it as a non-low-reliability month. It also produces:

- longitudinal-coverage and low-threshold sensitivity tables;
- persistence for MTA-reported availability and calendar continuity;
- January–October partial-year sensitivity;
- a 2015–2025 common-asset panel;
- borough excluded-time concentration;
- cross-scale borough rank concordance.

Station coordinates are generated directly from official MTA dataset `5f5g-n3cz`. The core analysis uses the frozen 16 November 2026 data snapshot. The normal reproduction workflow is manual-only.
