"""Common-support fixed-capacity screening for the TR-A analysis."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def screening_sets(cm: pd.DataFrame, q: float):
    x = cm[
        cm["reported_availability"].notna()
        & cm["calendar_continuity"].notna()
    ].copy()

    monthly = []
    flags = []

    for month, g in x.groupby("Month", sort=True):
        g = g.copy()
        n = int(np.floor(q * len(g)))
        if n < 1:
            continue

        a = g.sort_values(
            ["reported_availability", "Station Complex MRN"]
        ).head(n)
        c = g.sort_values(
            ["calendar_continuity", "Station Complex MRN"]
        ).head(n)

        a_ids = set(a["Station Complex MRN"])
        c_ids = set(c["Station Complex MRN"])
        shared = a_ids & c_ids

        monthly.append({
            "Month": month,
            "common_support_n": len(g),
            "target_n": n,
            "shared_n": len(shared),
            "overlap": len(shared) / n,
            "exact_agreement": a_ids == c_ids,
        })

        for _, row in g.iterrows():
            cid = row["Station Complex MRN"]
            flags.append({
                "Month": month,
                "Station Complex MRN": cid,
                "Station Complex Name": row["Station Complex Name"],
                "Borough": row["Borough"],
                "reported_flag": int(cid in a_ids),
                "continuity_flag": int(cid in c_ids),
            })

    return pd.DataFrame(monthly), pd.DataFrame(flags)


def recurrence(flags: pd.DataFrame, min_months: int = 36):
    out = flags.groupby(
        ["Station Complex MRN", "Station Complex Name", "Borough"],
        dropna=False,
    ).agg(
        comparable_months=("Month", "nunique"),
        reported_recurrence=("reported_flag", "mean"),
        continuity_recurrence=("continuity_flag", "mean"),
    ).reset_index()

    out = out[out["comparable_months"] >= min_months].copy()
    out["recurrence_difference"] = (
        out["continuity_recurrence"] - out["reported_recurrence"]
    )
    return out.sort_values("recurrence_difference").reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--complex-month", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cm = pd.read_csv(args.complex_month, parse_dates=["Month"])
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    summaries = []
    quartile = None

    for q, label in [
        (0.20, "bottom quintile"),
        (0.25, "bottom quartile"),
        (1 / 3, "bottom tercile"),
    ]:
        monthly, flags = screening_sets(cm, q)
        rec = recurrence(flags)
        summaries.append({
            "screen": label,
            "q": q,
            "months": len(monthly),
            "mean_common_support_n": monthly["common_support_n"].mean(),
            "mean_target_n": monthly["target_n"].mean(),
            "mean_shared_n": monthly["shared_n"].mean(),
            "mean_overlap": monthly["overlap"].mean(),
            "exact_agreement_share": monthly["exact_agreement"].mean(),
            "eligible_complexes": len(rec),
        })
        if np.isclose(q, 0.25):
            quartile = rec

    pd.DataFrame(summaries).to_csv(
        outdir / "common_support_screening_summary.csv", index=False
    )
    quartile.to_csv(
        outdir / "common_support_recurrence_quartile.csv", index=False
    )


if __name__ == "__main__":
    main()
