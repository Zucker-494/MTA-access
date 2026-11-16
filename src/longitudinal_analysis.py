"""Longitudinal MTA elevator service-continuity analysis.

CPU-only reproducible analysis for the Journal of Transport Geography manuscript.

Primary distinction
-------------------
MTA-reported availability = available hours / MTA-reported denominator hours
calendar continuity       = available hours / calendar hours in the asset-month

Calendar continuity is an asset-service measure. It is not a passenger-level
step-free journey probability.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr
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
        "24-Hour Hours Available", "24-Hour Total Hours", "Time Since Major Improvement",
    ]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d["reported_availability"] = parse_pct(d["24-Hour Availability"])

    e = d[d["Equipment Type"].astype(str).str.strip().str.lower().eq("elevator")].copy()
    e["calendar_hours"] = e["Month"].dt.days_in_month * 24
    e["calendar_continuity"] = e["24-Hour Hours Available"] / e["calendar_hours"]
    e["excluded_hours"] = (e["calendar_hours"] - e["24-Hour Total Hours"]).clip(lower=0)
    e["excluded_share"] = e["excluded_hours"] / e["calendar_hours"]
    e["third_party"] = e["Managed By"].astype(str).str.contains(
        "Third", case=False, na=False
    ).astype(int)
    e["year"] = e["Month"].dt.year

    assert e.duplicated(["Equipment Code", "Month"]).sum() == 0
    recalc = e["24-Hour Hours Available"] / e["24-Hour Total Hours"].replace(0, np.nan)
    assert (recalc - e["reported_availability"]).abs().max() < 1e-9
    return e


def annual_metrics(e: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    keys = ["year"] if by is None else ["year", by]
    g = e.groupby(keys, dropna=False).agg(
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
        excluded_hours=("excluded_hours", "sum"),
        n_elevators=("Equipment Code", "nunique"),
        third_party_share=("third_party", "mean"),
    ).reset_index()
    x["reported_availability"] = x["hours_available"] / x["reported_hours"].replace(0, np.nan)
    x["calendar_continuity"] = x["hours_available"] / x["calendar_hours"]
    x["excluded_share"] = 1 - x["reported_hours"] / x["calendar_hours"]
    return x


def _low_indicator(x: pd.DataFrame, metric: str, quantile: float) -> pd.Series:
    """Return 1/0 for valid metric values and NaN where the metric is missing."""
    rank = x.groupby("Month")[metric].rank(
        method="average", pct=True, ascending=True, na_option="keep"
    )
    out = pd.Series(np.nan, index=x.index, dtype="float64")
    valid = rank.notna()
    out.loc[valid] = (rank.loc[valid] <= quantile).astype(float)
    return out


def chronicity(
    cm: pd.DataFrame, min_months: int = 36, quantile: float = 0.25
) -> pd.DataFrame:
    """Monthly low-reliability recurrence, preserving missing reported metrics."""
    x = cm.copy()
    x["reported_low"] = _low_indicator(x, "reported_availability", quantile)
    x["continuity_low"] = _low_indicator(x, "calendar_continuity", quantile)

    out = x.groupby(
        ["Station Complex MRN", "Station Complex Name", "Borough"], dropna=False
    ).agg(
        n_months=("Month", "nunique"),
        n_reported_valid=("reported_availability", "count"),
        n_continuity_valid=("calendar_continuity", "count"),
        reported_bq_share=("reported_low", "mean"),
        continuity_bq_share=("continuity_low", "mean"),
        mean_excluded_share=("excluded_share", "mean"),
        mean_third_party_share=("third_party_share", "mean"),
    ).reset_index()
    out = out[out["n_months"] >= min_months].copy()
    out["bq_reclassification_delta"] = (
        out["continuity_bq_share"] - out["reported_bq_share"]
    )
    return out


def chronicity_coverage_sensitivity(cm: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for min_months in [24, 36, 48, 60, 72]:
        c = chronicity(cm, min_months=min_months, quantile=0.25)
        rho, _ = spearmanr(
            c["reported_bq_share"], c["continuity_bq_share"], nan_policy="omit"
        )
        delta = c["bq_reclassification_delta"]
        rows.append({
            "min_months": min_months,
            "n_complexes": len(c),
            "rho_chronic": rho,
            "max_delta": delta.max(),
            "n_delta_ge_0_15": int((delta >= 0.15).sum()),
            "n_continuity_low_ge_0_5": int((c["continuity_bq_share"] >= 0.50).sum()),
        })
    return pd.DataFrame(rows)


def chronicity_threshold_sensitivity(cm: pd.DataFrame) -> pd.DataFrame:
    """Vary the descriptive low-reliability cut point."""
    rows = []
    for q, name in [
        (0.20, "bottom quintile"),
        (0.25, "bottom quartile"),
        (1 / 3, "bottom tercile"),
    ]:
        c = chronicity(cm, min_months=36, quantile=q)
        rho, _ = spearmanr(
            c["reported_bq_share"], c["continuity_bq_share"], nan_policy="omit"
        )
        ids = sorted(
            c.loc[c["bq_reclassification_delta"] >= 0.15, "Station Complex MRN"]
            .dropna().astype(int).tolist()
        )
        rows.append({
            "threshold": name,
            "quantile": q,
            "n_complexes": len(c),
            "rho_chronic": rho,
            "n_delta_ge_0_15": len(ids),
            "n_continuity_low_ge_0_5": int((c["continuity_bq_share"] >= 0.50).sum()),
            "complex_ids_delta_ge_0_15": ";".join(map(str, ids)),
        })
    return pd.DataFrame(rows)


def loss_decomposition_2025(e: pd.DataFrame) -> pd.DataFrame:
    x = e[e["year"] == 2025].copy()
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


def boundary_month_sensitivity_2025(e: pd.DataFrame) -> pd.DataFrame:
    bounds = e.groupby("Equipment Code")["Month"].agg(
        first_observed_month="min", last_observed_month="max"
    ).reset_index()
    x = e.merge(bounds, on="Equipment Code", how="left", validate="many_to_one")
    primary = x[x["year"] == 2025].copy()
    trimmed = x[
        (x["Month"] != x["first_observed_month"])
        & (x["Month"] != x["last_observed_month"])
        & (x["year"] == 2025)
    ].copy()

    def summarize(label: str, g: pd.DataFrame) -> dict:
        available = g["24-Hour Hours Available"].sum()
        calendar = g["calendar_hours"].sum()
        return {
            "scenario": label,
            "n_observations": len(g),
            "n_equipment": g["Equipment Code"].nunique(),
            "hours_available": available,
            "calendar_hours": calendar,
            "calendar_continuity": available / calendar,
        }

    out = pd.DataFrame([
        summarize("Primary", primary),
        summarize("Exclude first and last observed month per elevator", trimmed),
    ])
    out["difference_from_primary_pp"] = 100 * (
        out["calendar_continuity"] - out.loc[0, "calendar_continuity"]
    )
    return out


def _rank_stability(
    cm: pd.DataFrame, metric: str, month_limit: int | None = None
) -> pd.DataFrame:
    x = cm.copy()
    if month_limit is not None:
        x = x[x["Month"].dt.month <= month_limit].copy()
    x["year"] = x["Month"].dt.year
    denominator = "reported_hours" if metric == "reported_availability" else "calendar_hours"
    a = x.groupby(["year", "Station Complex MRN"], dropna=False).agg(
        numerator=("hours_available", "sum"),
        denominator=(denominator, "sum"),
        months=("Month", "nunique"),
    ).reset_index()
    a["metric"] = a["numerator"] / a["denominator"].replace(0, np.nan)

    rows = []
    for y in range(int(a["year"].min()), int(a["year"].max())):
        p = a[(a["year"] == y) & (a["months"] >= 6)][
            ["Station Complex MRN", "metric"]
        ].dropna()
        q = a[(a["year"] == y + 1) & (a["months"] >= 6)][
            ["Station Complex MRN", "metric"]
        ].dropna()
        z = p.merge(q, on="Station Complex MRN", suffixes=("_a", "_b"))
        rho, pv = spearmanr(z["metric_a"], z["metric_b"])
        rows.append({
            "metric": metric,
            "month_window": "Jan-Oct" if month_limit == 10 else "available year",
            "year_1": y,
            "year_2": y + 1,
            "n_complexes": len(z),
            "spearman_rho": rho,
            "p_value": pv,
        })
    return pd.DataFrame(rows)


def rank_stability_all(cm: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        _rank_stability(cm, "reported_availability"),
        _rank_stability(cm, "calendar_continuity"),
        _rank_stability(cm, "reported_availability", month_limit=10),
        _rank_stability(cm, "calendar_continuity", month_limit=10),
    ], ignore_index=True)


def balanced_panel_sensitivity(e: pd.DataFrame) -> pd.DataFrame:
    """Common-asset sensitivity for complete 2015-2025 years."""
    x = e[e["year"].between(2015, 2025)].copy()
    months = x.groupby(["Equipment Code", "year"])["Month"].nunique().unstack(fill_value=0)
    years = list(range(2015, 2026))
    for y in years:
        if y not in months.columns:
            months[y] = 0
    balanced_ids = months.index[(months[years] >= 10).all(axis=1)]
    b = x[x["Equipment Code"].isin(balanced_ids)].copy()
    out = annual_metrics(b)
    out["balanced_equipment_count"] = len(balanced_ids)
    out["selection_rule"] = ">=10 observed months in every year, 2015-2025"
    return out


def borough_excluded_concentration_2025(e: pd.DataFrame) -> pd.DataFrame:
    rows = []
    x = e[e["year"] == 2025].copy()
    for borough, g in x.groupby("Borough"):
        c = g.groupby(
            ["Station Complex MRN", "Station Complex Name"], dropna=False
        ).agg(excluded_hours=("excluded_hours", "sum")).reset_index()
        c = c.sort_values("excluded_hours", ascending=False)
        total = c["excluded_hours"].sum()
        shares = c["excluded_hours"] / total if total > 0 else pd.Series(0.0, index=c.index)
        rows.append({
            "borough": borough,
            "n_complexes": len(c),
            "total_excluded_hours": total,
            "top1_share": shares.iloc[:1].sum(),
            "top3_share": shares.iloc[:3].sum(),
            "top5_share": shares.iloc[:5].sum(),
            "top_complex_id": int(c.iloc[0]["Station Complex MRN"]) if len(c) else np.nan,
            "top_complex_name": c.iloc[0]["Station Complex Name"] if len(c) else "",
        })
    return pd.DataFrame(rows)


def management_models(e: pd.DataFrame) -> pd.DataFrame:
    """Secondary exploratory analysis for the supplementary material."""
    r = e.dropna(
        subset=["reported_availability", "Station Complex MRN", "Equipment Code"]
    ).copy()
    r["month_fe"] = r["Month"].dt.strftime("%Y-%m")
    r["complex_fe"] = r["Station Complex MRN"].astype(str)

    def fit(formula: str, df: pd.DataFrame, name: str, cluster: pd.Series) -> dict:
        m = smf.ols(formula, data=df).fit(
            cov_type="cluster", cov_kwds={"groups": cluster}
        )
        ci = m.conf_int().loc["third_party"]
        return {
            "model": name,
            "n_obs": int(m.nobs),
            "n_equipment": df["Equipment Code"].nunique(),
            "n_complexes": df["Station Complex MRN"].nunique(),
            "third_party_coef": m.params["third_party"],
            "clustered_se": m.bse["third_party"],
            "p_value": m.pvalues["third_party"],
            "ci_low": ci.iloc[0],
            "ci_high": ci.iloc[1],
        }

    formula = "reported_availability ~ third_party + C(month_fe) + C(complex_fe)"
    rows = [
        fit(
            "reported_availability ~ third_party + C(month_fe) + C(Borough)",
            r,
            "Month FE + borough FE; elevator-clustered SE",
            r["Equipment Code"].astype(str),
        ),
        fit(
            formula,
            r,
            "Month FE + complex FE; elevator-clustered SE",
            r["Equipment Code"].astype(str),
        ),
        fit(
            formula,
            r,
            "Month FE + complex FE; complex-clustered SE",
            r["Station Complex MRN"].astype(str),
        ),
    ]
    g = r.groupby("Station Complex MRN")["third_party"].agg(["min", "max"])
    mixed = g.index[(g["min"] == 0) & (g["max"] == 1)]
    rm = r[r["Station Complex MRN"].isin(mixed)].copy()
    rows.append(
        fit(
            formula,
            rm,
            "Mixed-management complexes; elevator-clustered SE",
            rm["Equipment Code"].astype(str),
        )
    )
    return pd.DataFrame(rows)


def platform_comparison(
    e: pd.DataFrame, platform_path: str | Path
) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = pd.read_csv(platform_path)
    p["month"] = pd.to_datetime(p["month"], errors="coerce")
    p["availability"] = pd.to_numeric(p["availability"], errors="coerce")
    p = p[p["borough"].isin(["Bronx", "Brooklyn", "Manhattan", "Queens"])].copy()

    a = e[e["Month"].between(p["month"].min(), p["month"].max())].groupby(
        ["Month", "Borough"]
    ).agg(
        hours_available=("24-Hour Hours Available", "sum"),
        reported_hours=("24-Hour Total Hours", "sum"),
    ).reset_index()
    a["asset_reported"] = a["hours_available"] / a["reported_hours"].replace(0, np.nan)
    z = p.merge(a, left_on=["month", "borough"], right_on=["Month", "Borough"])

    pr = pearsonr(z["asset_reported"], z["availability"])
    sr = spearmanr(z["asset_reported"], z["availability"])
    monthly = []
    for month, g in z.groupby("month"):
        if len(g) != 4:
            continue
        g = g.copy()
        g["asset_rank"] = g["asset_reported"].rank(method="average", ascending=False)
        g["platform_rank"] = g["availability"].rank(method="average", ascending=False)
        tau, _ = kendalltau(g["asset_rank"], g["platform_rank"])
        monthly.append({
            "month": month,
            "kendall_tau": tau,
            "exact_full_ranking": bool((g["asset_rank"] == g["platform_rank"]).all()),
            "n_borough_rank_changes": int(
                (g["asset_rank"] != g["platform_rank"]).sum()
            ),
        })
    monthly = pd.DataFrame(monthly)

    summary = pd.DataFrame([{
        "n_borough_months": len(z),
        "pearson_r": pr.statistic,
        "spearman_rho": sr.statistic,
        "mae_percentage_points": 100 * np.mean(
            np.abs(z["asset_reported"] - z["availability"])
        ),
        "asset_minus_platform_bias_pp": 100 * np.mean(
            z["asset_reported"] - z["availability"]
        ),
        "months_with_exact_four_borough_ranking": int(
            monthly["exact_full_ranking"].sum()
        ),
        "months_total": len(monthly),
        "exact_ranking_share": monthly["exact_full_ranking"].mean(),
        "mean_kendall_tau": monthly["kendall_tau"].mean(),
        "share_borough_month_positions_changed": (
            monthly["n_borough_rank_changes"].sum() / (4 * len(monthly))
        ),
    }])
    return summary, monthly


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

    annual_metrics(e).to_csv(out / "system_yearly.csv", index=False)
    annual_metrics(e, "Managed By").to_csv(out / "management_yearly.csv", index=False)
    annual_metrics(e, "Borough").to_csv(out / "borough_yearly.csv", index=False)
    cm.to_csv(out / "complex_month.csv", index=False)
    chronicity(cm, 36, 0.25).to_csv(out / "complex_chronicity.csv", index=False)
    chronicity_coverage_sensitivity(cm).to_csv(
        out / "chronicity_sensitivity.csv", index=False
    )
    chronicity_threshold_sensitivity(cm).to_csv(
        out / "chronicity_threshold_sensitivity.csv", index=False
    )
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
    management_models(e).to_csv(out / "management_regression.csv", index=False)
    summary, monthly = platform_comparison(e, args.platform)
    summary.to_csv(out / "platform_comparison.csv", index=False)
    monthly.to_csv(out / "platform_rank_concordance_monthly.csv", index=False)

    print(f"elevator rows: {len(e):,}")
    print(f"equipment: {e['Equipment Code'].nunique()}")
    print(f"complexes: {e['Station Complex MRN'].nunique()}")


if __name__ == "__main__":
    main()
