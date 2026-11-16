# JTG manuscript workspace

Primary target: **Journal of Transport Geography**.

Working title:

**Reliability or continuity? How measurement changes the geography of New York subway elevator service**

The blinded manuscript uses Elsevier's `elsarticle` class with author-year references. The title page is kept separate for double-anonymized review.

## Manuscript files

- `manuscript_blind.tex` — blinded master LaTeX file.
- `01_introduction_background.tex` — introduction and conceptual background.
- `02_data_methods.tex` — data, measurement framework, spatial analysis, and reproducibility.
- `03_results.tex` — verified empirical results and sensitivity checks.
- `04_discussion_conclusion.tex` — discussion, transferability, limitations, and conclusions.
- `references.bib` — BibTeX database.
- `highlights.txt` — four JTG/Elsevier highlights.
- `figure_captions.txt` — separate caption file in manuscript figure-number order.
- `title_page_template.tex` — non-blinded title-page template.
- `cover_letter_template.txt` — working cover letter.
- `CRediT_template.txt` — authorship-contribution template.
- `submission_checklist.md` — final author-input and submission checks.

## Figures

The repository `figures/` directory contains the five 300 dpi main-text PNGs and two supplementary PNGs.

Manuscript order is:

1. `fig2_metric_gap.png`
2. `fig1_spatial.png`
3. `fig3_reclassification.png`
4. `fig4_persistence.png`
5. `fig5_validation.png`

The two supplementary graphics are `figS1_management_availability.png` and `figS2_borough_metric_gap.png`.

## Flat Editorial Manager working package

After figures are reproduced, run:

```bash
python manuscript/build_submission.py \
  --figures-dir figures \
  --output submission_flat
```

The script creates one flat working directory containing the manuscript source, bibliography, submission-support files, five main figures, and two supplementary figures. Compile and visually inspect the PDF before upload.

## Reproducibility status

The numerical pipeline is CPU-only. A successful frozen-data workflow reproduced the five main figures and two supplementary figures at 300 dpi and published those verified PNGs to the repository. The GitHub Actions workflow is now manual-only, so normal manuscript or code commits do not consume Actions minutes.
