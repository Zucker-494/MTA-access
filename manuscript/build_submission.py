"""Build a flat Elsevier/JTG LaTeX submission directory.

Editorial Manager does not support LaTeX subfolders. This script copies the
blinded manuscript, section files, bibliography, highlights and generated
figures to one directory without altering scientific content.
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
]
FIGURES = [
    "fig1_spatial.png",
    "fig2_metric_gap.png",
    "fig3_reclassification.png",
    "fig4_persistence.png",
    "fig5_validation.png",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript-dir", type=Path, default=Path(__file__).parent)
    ap.add_argument("--figures-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    for name in TEXT_FILES:
        src = args.manuscript_dir / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, args.output / name)

    for name in FIGURES:
        src = args.figures_dir / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, args.output / name)

    print(f"Flat JTG submission source prepared at: {args.output}")


if __name__ == "__main__":
    main()
