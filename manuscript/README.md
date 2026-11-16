# JTG manuscript workspace

Primary target: **Journal of Transport Geography**.

The blinded manuscript uses Elsevier's `elsarticle` class with author-year
references. The title page is kept separate for double-anonymized review.

## Main files

- `manuscript_blind.tex` — blinded master LaTeX file.
- `01_introduction_background.tex` — introduction and conceptual background.
- `02_data_methods.tex` — data, metrics and spatial analysis.
- `03_results.tex` — verified empirical results.
- `04_discussion_conclusion.tex` — discussion, limitations and conclusions.
- `references.bib` — BibTeX database.
- `highlights.txt` — four concise highlights.
- `title_page_template.tex` — separate non-blinded title-page template.

## Flat Editorial Manager package

Elsevier's Editorial Manager LaTeX processing does not accept subfolders.
After figures are reproduced, run:

```
python manuscript/build_submission.py \
  --figures-dir <path-to-generated-figures> \
  --output submission_flat
```

The resulting directory contains all manuscript source and five main figures at
one folder level. Compile and inspect the PDF before submission.
