"""Create JTG-oriented 300 dpi figures from verified analysis outputs.

Five main figures and two supplementary figures are generated. Highlight
categories are mutually exclusive, annotation text never covers data points,
and the cross-scale comparison is shown as monthly rank concordance rather
than an overplotted scatter cloud.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def style() -> None:
    plt.rcParams.update({
        "font.size": 9.5,
        "axes.labelsize": 10,
        "legend.fontsize": 8.3,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.7,
        "savefig.bbox": "tight",
    })


def finish(ax: plt.Axes, path: Path, grid: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(axis="y", alpha=0.16, linewidth=0.6)
    plt.tight_layout()
    plt.savefig(path, dpi=300, format="png")
    plt.close()


def _geometry_exteriors(geometry: dict) -> list[np.ndarray]:
    """Return exterior rings for Polygon/MultiPolygon GeoJSON geometries."""
    typ = geometry.get("type")
    coords = geometry.get("coordinates", [])
    polygons = [coords] if typ == "Polygon" else coords if typ == "MultiPolygon" else []
    out = []
    for polygon in polygons:
        if not polygon:
            continue
        exterior = np.asarray(polygon[0], dtype=float)
        if exterior.ndim == 2 and exterior.shape[1] == 2:
            out.append(exterior)
    return out


def spatial_figure(
    ch: pd.DataFrame,
    stations_path: Path,
    borough_geojson: Path,
    out: Path,
) -> None:
    st = pd.read_csv(stations_path)
    required = {"complex_id", "latitude", "longitude"}
    missing = required.difference(st.columns)
    if missing:
        raise ValueError(f"Station coordinate file missing columns: {sorted(missing)}")

    st["complex_id"] = pd.to_numeric(st["complex_id"], errors="coerce")
    x = ch.copy()
    x["Station Complex MRN"] = pd.to_numeric(x["Station Complex MRN"], errors="coerce")
    z = x.merge(
        st,
        left_on="Station Complex MRN",
        right_on="complex_id",
        how="left",
        validate="many_to_one",
    )
    if z[["latitude", "longitude"]].isna().any().any():
        miss = z.loc[z["latitude"].isna(), "Station Complex MRN"].dropna().unique()
        raise ValueError(f"Missing coordinates for complexes: {miss[:20]}")

    chronic = z["continuity_bq_share"] >= 0.50
    reclass = z["bq_reclassification_delta"] >= 0.15
    category = np.select(
        [
            chronic & reclass,
            chronic & ~reclass,
            ~chronic & reclass,
        ],
        ["Both diagnostics", "Persistent low continuity", "Strong reclassification"],
        default="Other long-observed complex",
    )
    z["map_category"] = category

    with open(borough_geojson, "r", encoding="utf-8") as fh:
        gj = json.load(fh)

    fig, ax = plt.subplots(figsize=(7.4, 6.0))
    bx, by = [], []
    for feature in gj.get("features", []):
        for exterior in _geometry_exteriors(feature.get("geometry", {})):
            bx.extend(exterior[:, 0].tolist())
            by.extend(exterior[:, 1].tolist())
            bx.append(np.nan)
            by.append(np.nan)
    ax.plot(bx, by, linewidth=0.55, alpha=0.35, zorder=1)

    # Sizes are deliberately small enough to avoid point-on-point overlap in
    # the dense Manhattan portion of the map. Categories are mutually exclusive.
    specs = [
        ("Other long-observed complex", "o", 2),
        ("Persistent low continuity", "^", 6),
        ("Strong reclassification", "s", 6),
        ("Both diagnostics", "*", 9),
    ]
    for label, marker, size in specs:
        g = z[z["map_category"] == label]
        if g.empty:
            continue
        ax.scatter(
            g["longitude"], g["latitude"],
            s=size, marker=marker, label=label, zorder=3,
        )

    mean_lat = float(z["latitude"].mean())
    ax.set_aspect(1 / np.cos(np.deg2rad(mean_lat)))

    xmin, xmax = z["longitude"].min(), z["longitude"].max()
    ymin, ymax = z["latitude"].min(), z["latitude"].max()
    x0 = xmin + 0.04 * (xmax - xmin)
    y0 = ymin + 0.04 * (ymax - ymin)
    km5_lon = 5.0 / (111.32 * np.cos(np.deg2rad(mean_lat)))
    ax.plot([x0, x0 + km5_lon], [y0, y0], linewidth=1.4, zorder=6)
    ax.text(
        x0 + km5_lon / 2,
        y0 + 0.012 * (ymax - ymin),
        "5 km",
        ha="center",
        va="bottom",
        fontsize=7.5,
    )
    ax.annotate(
        "N",
        xy=(0.94, 0.96),
        xytext=(0.94, 0.86),
        xycoords="axes fraction",
        textcoords="axes fraction",
        ha="center",
        va="center",
        arrowprops=dict(arrowstyle="-|>", linewidth=0.9),
        fontsize=8.5,
    )

    ax.set_xlim(-74.06, -73.73)
    ax.set_ylim(40.55, 40.93)
    ax.set_axis_off()
    ax.legend(
        frameon=False,
        fontsize=7.5,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0,
        markerscale=3.0,
    )
    plt.tight_layout()
    plt.savefig(out, dpi=300, format="png")
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--main", type=Path, required=True)
    ap.add_argument("--platform", type=Path, required=True)
    ap.add_argument("--stations", type=Path, required=True)
    ap.add_argument("--borough-boundaries", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    style()

    ys = pd.read_csv(args.results / "system_yearly.csv")
    ch = pd.read_csv(args.results / "complex_chronicity.csv")
    rs = pd.read_csv(args.results / "rank_stability.csv")
    concord = pd.read_csv(
        args.results / "platform_rank_concordance_monthly.csv",
        parse_dates=["month"],
    )
    reg = pd.read_csv(args.results / "management_regression.csv")

    # Figure 1 — spatial chronicity and metric-induced reclassification.
    spatial_figure(
        ch,
        args.stations,
        args.borough_boundaries,
        args.output / "fig1_spatial.png",
    )

    # Figure 2 — central measurement gap.
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(
        ys["year"],
        100 * ys["reported_availability"],
        marker="o",
        label="MTA-reported availability",
    )
    ax.plot(
        ys["year"],
        100 * ys["calendar_continuity"],
        marker="s",
        label="Calendar continuity",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Service measure (%)")
    ax.legend(frameon=False, loc="upper left")
    ax.set_xticks(ys["year"])
    ax.tick_params(axis="x", rotation=45)
    finish(ax, args.output / "fig2_metric_gap.png")

    # Figure 3 — sorted recurrence difference. Bars occupy unique x positions,
    # avoiding point-on-point and label-on-point overlap.
    d = ch.sort_values("bq_reclassification_delta").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    x = np.arange(len(d))
    ax.bar(x, d["bq_reclassification_delta"], width=0.72)
    ax.set_xlabel("Station complexes ordered by recurrence difference")
    ax.set_ylabel("Calendar − MTA-reported recurrence")
    ax.set_xticks([])
    finish(ax, args.output / "fig3_reclassification.png")

    # Figure 4 — adjacent-year persistence for the operator-reported baseline.
    r = rs[
        (rs["metric"] == "reported_availability")
        & (rs["month_window"] == "available year")
    ].copy()
    labels = [f"{a}–{b}" for a, b in zip(r["year_1"], r["year_2"])]
    fig, ax = plt.subplots(figsize=(6.2, 3.7))
    ax.plot(range(len(r)), r["spearman_rho"], marker="o")
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("Adjacent year pair")
    ax.set_ylabel("Spearman rank correlation")
    finish(ax, args.output / "fig4_persistence.png")

    # Figure 5 — monthly spatial concordance between asset and platform metrics.
    # One observation per month avoids the overplotting in the previous
    # borough-month scatter representation.
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(concord["month"], concord["kendall_tau"])
    ax.set_xlabel("Month")
    ax.set_ylabel("Kendall rank concordance")
    ax.set_ylim(-1.05, 1.05)
    finish(ax, args.output / "fig5_concordance.png")

    # Supplementary Figure S1 — governance coefficients, not overlapping trends.
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    y = np.arange(len(reg))
    coef = 100 * reg["third_party_coef"]
    lo = 100 * reg["ci_low"]
    hi_ci = 100 * reg["ci_high"]
    xerr = np.vstack([coef - lo, hi_ci - coef])
    labels = [
        "Borough FE; elevator-clustered",
        "Complex FE; elevator-clustered",
        "Complex FE; complex-clustered",
        "Mixed complexes; elevator-clustered",
    ]
    ax.errorbar(coef, y, xerr=xerr, fmt="o", capsize=3)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Third-party coefficient (percentage points)")
    ax.set_ylabel("")
    ax.invert_yaxis()
    finish(ax, args.output / "figS1_management_coefficients.png", grid=False)

    # Supplementary Figure S2 — calendar-continuity rank persistence.
    rc = rs[
        (rs["metric"] == "calendar_continuity")
        & (rs["month_window"] == "available year")
    ].copy()
    labels_c = [f"{a}–{b}" for a, b in zip(rc["year_1"], rc["year_2"])]
    fig, ax = plt.subplots(figsize=(6.2, 3.7))
    ax.plot(range(len(rc)), rc["spearman_rho"], marker="o")
    ax.set_xticks(range(len(labels_c)), labels_c, rotation=45, ha="right")
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("Adjacent year pair")
    ax.set_ylabel("Spearman rank correlation")
    finish(ax, args.output / "figS2_calendar_persistence.png")


if __name__ == "__main__":
    main()
