"""Main analysis workflow for the TR-A manuscript.

This script produces only the descriptive and sensitivity outputs used in the
TR-A manuscript. Common-support screening is run separately with
src/common_support_analysis.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from longitudinal_analysis import (
    annual_metrics,
    balanced_panel_sensitivity,
    boundary_month_sensitivity_2025,
    borough_excluded_concentration_2025,
    complex_month,
    load_elevators,
    loss_decomposition_2025,
    rank_stability_all,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    e = load_elevators(args.main)
    cm = complex_month(e)

    annual_metrics(e).to_csv(out / "system_yearly.csv", index=False)
    annual_metrics(e, "Borough").to_csv(out / "borough_yearly.csv", index=False)
    cm.to_csv(out / "complex_month.csv", index=False)
    loss_decomposition_2025(e).to_csv(
        out / "loss_decomposition_2025.csv", index=False
    )
    boundary_month_sensitivity_2025(e).to_csv(
        out / "boundary_month_sensitivity_2025.csv", index=False
    )
    rank_stability_all(cm).to_csv(out / "rank_stability.csv", index=False)
    balanced_panel_sensitivity(e).to_csv(
        out / "balanced_panel_system_yearly.csv", index=False
    )
    borough_excluded_concentration_2025(e).to_csv(
        out / "borough_excluded_concentration_2025.csv", index=False
    )

    print(f"elevator rows: {len(e):,}")
    print(f"equipment: {e['Equipment Code'].nunique()}")
    print(f"complexes: {e['Station Complex MRN'].nunique()}")


if __name__ == "__main__":
    main()
