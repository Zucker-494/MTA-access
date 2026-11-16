"""Build a flat Elsevier/JTG working submission directory.

Editorial Manager LaTeX processing is safest when all source files and artwork
are at one directory level. The script copies the blinded manuscript source,
submission-support files, five main figures, and two supplementary figures.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

TEXT_FILES = [
    "manuscript_blind.tex",
    "01_introduction_background.tex",
    "02_data_methods.tex",
    "03_results.tex",
    "04_discussion_conclusion.tex",
    "references.bib",
    "highlights.txt",
    "figure_captions.txt",
    "title_page_template.tex",
    "cover_letter_template.txt",
    "CRediT_template.txt",
    "submission_checklist.md",
]

MAIN_FIGURES = [
    "fig1_spatial.png",
    "fig2_metric_gap.png",
    "fig3_reclassification.png",
    "fig4_persistence.png",
    "fig5_validation.png",
]

SUPPLEMENTARY_FIGURES = [
    "figS1_management_availability.png",
    "figS2_borough_metric_gap.png",
]


def copy_required(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    shutil.copy2(src, dst)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript-dir", type=Path, default=Path(__file__).parent)
    ap.add_argument("--figures-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument(
        "--without-supplementary",
        action="store_true",
        help="Copy only the five main-text figures.",
    )
    args = ap.parse_args()

    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)

    for name in TEXT_FILES:
        copy_required(args.manuscript_dir / name, args.output / name)

    figures = list(MAIN_FIGURES)
    if not args.without_supplementary:
        figures.extend(SUPPLEMENTARY_FIGURES)
    for name in figures:
        copy_required(args.figures_dir / name, args.output / name)

    print(f"Flat JTG working submission source prepared at: {args.output}")
    print(f"Copied {len(TEXT_FILES)} text/support files and {len(figures)} figures.")


if __name__ == "__main__":
    main()
