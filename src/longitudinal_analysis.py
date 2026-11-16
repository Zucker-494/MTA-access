"""Longitudinal MTA elevator reliability analysis.

CPU-only. No GitHub Actions required.

The central distinction is:
reported availability = available hours / MTA-reported denominator hours
calendar continuity   = available hours / calendar hours

Calendar continuity is an asset-service sensitivity measure, not passenger-level
step-free journey success.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr, kendalltau
import statsmodels.formula.api as smf


def parse_pct(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip()
    pct = x.str.contains("%", regex=False)
    v = pd.to_numeric(x.str.replace("%", "", regex=False), errors="coerce")
    v.loc[pct] = v.loc[pct] / 100.0
    return v


def load_elevators(path: str | Path) -> pd.DataFrame:
    d = pd.read_csv(path, low_memory=False)
    d["Month"] = pd.to_datetime(d["Month"], errors="coerce")
    for c in [
        "Total Outages", "Scheduled Outages", "Unscheduled Outages", "Entrapments",
        "24-Hour Hours Available", "24-Hour Total Hours"
    ]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["reported_availability"] = parse_pct(d["24-Hour Availability"])

    e = d[d["Equipment Type"].astype(str).str.strip().str.lower().eq("elevator")].copy()
    e["calendar_hours"] = e["Month"].dt.days_in_month * 24
    e["calendar_continuity"] = e["24-Hour Hours Available"] / e["calendar_hours"]
    e["excluded_hours"] = (e["calendar_hours"] - e["24-Hour Total Hours"]).clip(lower=0)
    e["excluded_share"] = e["excluded_hours"] / e["calendar_hours"]
    e["third_party"] = e["Managed By"].astype(str).str.contains("Third", case=False, na=False).astype(int)

    assert e.duplicated(["Equipment Code", "Month"]).sum() == 0
    recalc = e["24-Hour Hours Available"] / e["24-Hour Total Hours"].replace(0, np.nan)
    assert (recalc - e["reported_availability"]).abs().max() < 1e-9
    return e


def annual_metrics(e: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    x = e.copy()
    x["year"] = x["Month"].dt.year
    keys = ["year"] if by is None else ["year", by]
    g = x.groupby(keys, dropna=False).agg(
        hours_available=("24-Hour Hours Available", "sum"),
        reported_hours=("24-Hour Total Hours", "sum"),
        calendar_hours=("calendar_hours", "sum"),
        n_equipment=("Equipment Code", "nunique"),
        n_complexes=("Station Complex MRN", "nunique"),
    ).reset_index()
    g["reported_availability"] = g["hours_available"] / g["reported_hours"].replace(0, np.nan)
    g["calendar_continuity"] = g["hours_available"] / g["calendar_hours"]
    g["metric_gap_pp"] = 100 * (g["reported_availability"] - g["calendar_continuity"])
    g["excluded_denominator_share"] = 1 - g["reported_hours"] / g["calendar_hours"]
    return g


def complex_month(e: pd.DataFrame) -> pd.DataFrame:
    x = e.groupby(
        ["Month", "Station Complex MRN", "Station Complex Name", "Borough"], dropna=False
    ).agg(
        hours_available=("24-Hour Hours Available", "sum"),
        reported_hours=("24-Hour Total Hours", "sum"),
        calendar_hours=("calendar_hours", "sum"),
        n_elevators=("Equipment Code", "nunique"),
        third_party_share=("third_party", "mean"),
    ).reset_index()
    x["reported_availability"] = x["hours_available"] / x["reported_hours"].replace(0, np.nan)
    x["calendar_continuity"] = x["hours_available"] / x["calendar_hours"]
    x["excluded_share"] = 1 - x["reported_hours"] / x["calendar_hours"]
    return x



def chronicity(cm: pd.DataFrame, min_months: int = 36) -> pd.DataFrame:
    """Frequency with which a complex falls in each metric's monthly bottom quartile."""
    x = cm.copy()
    for metric in ["reported_availability", "calendar_continuity"]:
        x[f"{metric}_pct_rank"] = x.groupby("Month")[metric].rank(
            method="average", pct=True, ascending=True
        )
        x[f"{metric}_bottom_quartile"] = x[f"{metric}_pct_rank"] <= 0.25
    out = x.groupby(
        ["Station Complex MRN", "Station Complex Name", "Borough"], dropna=False
    ).agg(
        n_months=("Month", "nunique"),
        reported_bq_share=("reported_availability_bottom_quartile", "mean"),
        continuity_bq_share=("calendar_continuity_bottom_quartile", "mean"),
        mean_excluded_share=("excluded_share", "mean"),
        mean_third_party_share=("third_party_share", "mean"),
    ).reset_index()
    out = out[out["n_months"] >= min_months].copy()
    out["bq_reclassification_delta"] = (
        out["continuity_bq_share"] - out["reported_bq_share"]
    )
    return out


def chronicity_sensitivity(cm: pd.DataFrame) -> pd.DataFrame:
    """Check that the spatial result is stable to longitudinal-coverage choice."""
    rows = []
    for min_months in [24, 36, 48, 60, 72]:
        c = chronicity(cm, min_months)
        rho, _ = spearmanr(c["reported_bq_share"], c["continuity_bq_share"])
        delta = c["bq_reclassification_delta"]
        rows.append([
            min_months, len(c), rho, delta.max(),
            int((delta >= 0.15).sum()),
            int((c["continuity_bq_share"] >= 0.50).sum()),
        ])
    return pd.DataFrame(rows, columns=[
        "min_months", "n_complexes", "rho_chronic", "max_delta",
        "n_delta_ge_0_15", "n_continuity_bq_ge_0_5",
    ])


def loss_decomposition_2025(e: pd.DataFrame) -> pd.DataFrame:
    """Decompose calendar service loss into within-denominator and excluded time."""
    x = e[e["Month"].dt.year == 2025].copy()
    x["within_reported_loss"] = (
        x["24-Hour Total Hours"] - x["24-Hour Hours Available"]
    ).clip(lower=0)
    rows = []
    for scope, g in [("System", x), *list(x.groupby("Borough"))]:
        calendar = g["calendar_hours"].sum()
        within = g["within_reported_loss"].sum()
        excluded = g["excluded_hours"].sum()
        available = g["24-Hour Hours Available"].sum()
        total_loss = within + excluded
        rows.append({
            "scope": scope,
            "available_share": available / calendar,
            "within_reported_loss_share": within / calendar,
            "excluded_loss_share": excluded / calendar,
            "excluded_fraction_of_total_loss": excluded / total_loss,
        })
    return pd.DataFrame(rows)


def rank_stability(cm: pd.DataFrame) -> pd.DataFrame:
    x = cm.copy()
    x["year"] = x["Month"].dt.year
    a = x.groupby(
        ["year", "Station Complex MRN", "Station Complex Name", "Borough"], dropna=False
    ).agg(
        hours_available=("hours_available", "sum"),
        reported_hours=("reported_hours", "sum"),
        months=("Month", "nunique"),
    ).reset_index()
    a["reported_availability"] = a["hours_available"] / a["reported_hours"].replace(0, np.nan)

    out = []
    for y in range(int(a.year.min()), int(a.year.max())):
        p = a[(a.year == y) & (a.months >= 6)][["Station Complex MRN", "reported_availability"]].dropna()
        q = a[(a.year == y + 1) & (a.months >= 6)][["Station Complex MRN", "reported_availability"]].dropna()
        z = p.merge(q, on="Station Complex MRN", suffixes=("_a", "_b"))
        rho, pv = spearmanr(z.reported_availability_a, z.reported_availability_b)
        out.append([y, y + 1, len(z), rho, pv])
    return pd.DataFrame(out, columns=["year_1", "year_2", "n_complexes", "spearman_rho", "p_value"])


def management_models(e: pd.DataFrame) -> pd.DataFrame:
    r = e.dropna(subset=["reported_availability", "Station Complex MRN", "Equipment Code"]).copy()
    r["month_fe"] = r["Month"].dt.strftime("%Y-%m")
    r["complex_fe"] = r["Station Complex MRN"].astype(str)

    def fit(formula: str, df: pd.DataFrame, name: str) -> dict:
        m = smf.ols(formula, data=df).fit(
            cov_type="cluster", cov_kwds={"groups": df["Equipment Code"].astype(str)}
        )
        ci = m.conf_int().loc["third_party"]
        return dict(
            model=name, n_obs=int(m.nobs), n_equipment=df["Equipment Code"].nunique(),
            n_complexes=df["Station Complex MRN"].nunique(),
            third_party_coef=m.params["third_party"], clustered_se=m.bse["third_party"],
            p_value=m.pvalues["third_party"], ci_low=ci.iloc[0], ci_high=ci.iloc[1]
        )

    rows = [
        fit("reported_availability ~ third_party + C(month_fe) + C(Borough)",
            r, "Month FE + borough FE"),
        fit("reported_availability ~ third_party + C(month_fe) + C(complex_fe)",
            r, "Month FE + complex FE"),
    ]
    g = r.groupby("Station Complex MRN")["third_party"].agg(["min", "max"])
    mixed = g.index[(g["min"] == 0) & (g["max"] == 1)]
    rm = r[r["Station Complex MRN"].isin(mixed)].copy()
    rows.append(fit(
        "reported_availability ~ third_party + C(month_fe) + C(complex_fe)",
        rm, "Mixed-management complexes only"
    ))
    return pd.DataFrame(rows)


def platform_validation(e: pd.DataFrame, platform_path: str | Path) -> pd.DataFrame:
    p = pd.read_csv(platform_path)
    p["month"] = pd.to_datetime(p["month"])
    p["availability"] = pd.to_numeric(p["availability"], errors="coerce")
    p = p[p["borough"].isin(["Bronx", "Brooklyn", "Manhattan", "Queens"])]

    a = e[e["Month"].between(p.month.min(), p.month.max())].groupby(["Month", "Borough"]).agg(
        hours_available=("24-Hour Hours Available", "sum"),
        reported_hours=("24-Hour Total Hours", "sum")
    ).reset_index()
    a["asset_reported"] = a["hours_available"] / a["reported_hours"].replace(0, np.nan)
    z = p.merge(a, left_on=["month", "borough"], right_on=["Month", "Borough"])

    pr = pearsonr(z.asset_reported, z.availability)
    sr = spearmanr(z.asset_reported, z.availability)
    exact = []
    taus = []
    changed = 0
    for _, g in z.groupby("month"):
        if len(g) != 4:
            continue
        ar = g.asset_reported.rank(method="average", ascending=False)
        br = g.availability.rank(method="average", ascending=False)
        tau, _ = kendalltau(ar, br)
        taus.append(tau)
        exact.append(bool((ar.values == br.values).all()))
        changed += int((ar.values != br.values).sum())

    return pd.DataFrame([dict(
        n_borough_months=len(z),
        pearson_r=pr.statistic,
        spearman_rho=sr.statistic,
        mae_percentage_points=100*np.mean(np.abs(z.asset_reported-z.availability)),
        asset_minus_platform_bias_pp=100*np.mean(z.asset_reported-z.availability),
        months_with_exact_four_borough_ranking=sum(exact),
        months_total=len(exact),
        exact_ranking_share=np.mean(exact),
        mean_kendall_tau=np.mean(taus),
        share_borough_month_positions_changed=changed/(4*len(exact)),
    )])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--platform", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    e = load_elevators(args.main)
    cm = complex_month(e)

    annual_metrics(e).to_csv(out/"system_yearly.csv", index=False)
    annual_metrics(e, "Managed By").to_csv(out/"management_yearly.csv", index=False)
    annual_metrics(e, "Borough").to_csv(out/"borough_yearly.csv", index=False)
    cm.to_csv(out/"complex_month.csv", index=False)
    chronicity(cm, 36).to_csv(out/"complex_chronicity.csv", index=False)\n    chronicity_sensitivity(cm).to_csv(out/"chronicity_sensitivity.csv", index=False)\n    loss_decomposition_2025(e).to_csv(out/"loss_decomposition_2025.csv", index=False)\n    rank_stability(cm).to_csv(out/"rank_stability.csv", index=False)
    management_models(e).to_csv(out/"management_regression.csv", index=False)
    platform_validation(e, args.platform).to_csv(out/"platform_validation.csv", index=False)

    print(f"elevator rows: {len(e):,}")
    print(f"equipment: {e['Equipment Code'].nunique()}")
    print(f"complexes: {e['Station Complex MRN'].nunique()}")


if __name__ == "__main__":
    main()
