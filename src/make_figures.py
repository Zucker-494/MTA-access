"""Create JTG-oriented 300 dpi figures from verified analysis outputs.

The manuscript uses five main figures plus one supplementary management figure.
No network access is required when the frozen station-coordinate snapshot is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


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


def validation_points(main_path: Path, platform_path: Path) -> pd.DataFrame:
    d = pd.read_csv(main_path, low_memory=False)
    d["Month"] = pd.to_datetime(d["Month"], errors="coerce")
    d["24-Hour Hours Available"] = pd.to_numeric(
        d["24-Hour Hours Available"], errors="coerce"
    )
    d["24-Hour Total Hours"] = pd.to_numeric(
        d["24-Hour Total Hours"], errors="coerce"
    )
    e = d[
        d["Equipment Type"].astype(str).str.strip().str.lower().eq("elevator")
    ].copy()

    p = pd.read_csv(platform_path)
    p["month"] = pd.to_datetime(p["month"], errors="coerce")
    p["availability"] = pd.to_numeric(p["availability"], errors="coerce")
    p = p[p["borough"].isin(["Bronx", "Brooklyn", "Manhattan", "Queens"])]

    a = e[e["Month"].between(p["month"].min(), p["month"].max())].groupby(
        ["Month", "Borough"]
    ).agg(
        hours_available=("24-Hour Hours Available", "sum"),
        reported_hours=("24-Hour Total Hours", "sum"),
    ).reset_index()
    a["asset_reported"] = (
        a["hours_available"] / a["reported_hours"].replace(0, np.nan)
    )
    return p.merge(
        a, left_on=["month", "borough"], right_on=["Month", "Borough"], how="inner"
    )



def _draw_geometry(ax: plt.Axes, geometry: dict) -> None:
    """Draw Polygon/MultiPolygon GeoJSON without GIS-library dependencies."""
    typ = geometry.get("type")
    coords = geometry.get("coordinates", [])
    polygons = [coords] if typ == "Polygon" else coords if typ == "MultiPolygon" else []
    for polygon in polygons:
        if not polygon:
            continue
        exterior = np.asarray(polygon[0], dtype=float)
        if exterior.ndim != 2 or exterior.shape[1] != 2:
            continue
        ax.add_patch(Polygon(
            exterior, closed=True, facecolor="0.96", edgecolor="0.65", linewidth=0.55
        ))
        for ring in polygon[1:]:
            hole = np.asarray(ring, dtype=float)
            if hole.ndim == 2 and hole.shape[1] == 2:
                ax.add_patch(Polygon(
                    hole, closed=True, facecolor="white", edgecolor="0.75", linewidth=0.3
                ))


def spatial_figure(ch: pd.DataFrame, stations_path: Path, borough_geojson: Path, out: Path) -> None:
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

    with open(borough_geojson, "r", encoding="utf-8") as fh:
        gj = json.load(fh)

    fig, ax = plt.subplots(figsize=(5.5, 6.0))
    for feature in gj.get("features", []):
        _draw_geometry(ax, feature.get("geometry", {}))

    ax.scatter(
        z["longitude"], z["latitude"], s=14, alpha=0.30,
        label="Long-observed elevator complex"
    )
    ax.scatter(
        z.loc[chronic, "longitude"], z.loc[chronic, "latitude"],
        s=70, facecolors="none", linewidths=1.2,
        label="Continuity bottom quartile in ≥50% of months"
    )
    ax.scatter(
        z.loc[reclass, "longitude"], z.loc[reclass, "latitude"],
        s=54, marker="x", linewidths=1.2,
        label="Reclassification increase ≥0.15"
    )
    mean_lat = float(z["latitude"].mean())
    ax.set_aspect(1 / np.cos(np.deg2rad(mean_lat)))

    # Standard cartographic elements requested by JTG editorial guidance.
    xmin, xmax = z["longitude"].min(), z["longitude"].max()
    ymin, ymax = z["latitude"].min(), z["latitude"].max()
    x0 = xmin + 0.04 * (xmax - xmin)
    y0 = ymin + 0.04 * (ymax - ymin)
    km5_lon = 5.0 / (111.32 * np.cos(np.deg2rad(mean_lat)))
    ax.plot([x0, x0 + km5_lon], [y0, y0], linewidth=1.4, zorder=6)
    ax.text(x0 + km5_lon / 2, y0 + 0.012 * (ymax - ymin),
            "5 km", ha="center", va="bottom", fontsize=7.5)
    ax.annotate(
        "N", xy=(0.94, 0.96), xytext=(0.94, 0.86),
        xycoords="axes fraction", textcoords="axes fraction",
        ha="center", va="center",
        arrowprops=dict(arrowstyle="-|>", linewidth=0.9), fontsize=8.5,
    )

    ax.set_xlim(-74.06, -73.73)
    ax.set_ylim(40.55, 40.93)
    ax.set_axis_off()
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
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
    yb = pd.read_csv(args.results / "borough_yearly.csv")
    ym = pd.read_csv(args.results / "management_yearly.csv")
    ch = pd.read_csv(args.results / "complex_chronicity.csv")
    rs = pd.read_csv(args.results / "rank_stability.csv")
    vp = validation_points(args.main, args.platform)

    # Fig. 1 — spatial chronicity and metric-induced reclassification.
    spatial_figure(
        ch, args.stations, args.borough_boundaries,
        args.output / "fig1_spatial.png"
    )

    # Fig. 2 — central measurement gap.
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(
        ys["year"], 100 * ys["reported_availability"], marker="o",
        label="Reported in-service availability"
    )
    ax.plot(
        ys["year"], 100 * ys["calendar_continuity"], marker="s",
        label="Calendar service continuity"
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Availability / continuity (%)")
    ax.legend(frameon=False, loc="upper left")
    ax.set_xticks(ys["year"])
    ax.tick_params(axis="x", rotation=45)
    finish(ax, args.output / "fig2_metric_gap.png")

    # Fig. 3 — chronicity reclassification.
    fig, ax = plt.subplots(figsize=(5.4, 4.8))
    ax.scatter(ch["reported_bq_share"], ch["continuity_bq_share"], s=26, alpha=0.72)
    hi = max(ch["reported_bq_share"].max(), ch["continuity_bq_share"].max()) * 1.04
    ax.plot([0, hi], [0, hi], "--", linewidth=1.0, label="No change")
    labels = {
        328: "Cortlandt St",
        635: "South Ferry / Whitehall St",
        620: "Court St / Borough Hall",
    }
    top = ch.nlargest(3, "bq_reclassification_delta")
    for _, row in top.iterrows():
        cid = int(row["Station Complex MRN"])
        label = labels.get(cid, str(cid))
        ax.annotate(
            label,
            (row["reported_bq_share"], row["continuity_bq_share"]),
            xytext=(5, 4), textcoords="offset points", fontsize=7.3
        )
    ax.set_xlim(0, hi)
    ax.set_ylim(0, hi)
    ax.set_xlabel("Bottom-quartile recurrence\nreported availability")
    ax.set_ylabel("Bottom-quartile recurrence\ncalendar continuity")
    ax.legend(frameon=False, loc="lower right")
    finish(ax, args.output / "fig3_reclassification.png")

    # Fig. 4 — adjacent-year persistence.
    fig, ax = plt.subplots(figsize=(6.2, 3.7))
    labels = [f"{a}–{b}" for a, b in zip(rs["year_1"], rs["year_2"])]
    ax.plot(range(len(rs)), rs["spearman_rho"], marker="o")
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("Adjacent year pair")
    ax.set_ylabel("Spearman rank correlation")
    ax.text(
        0.02, 0.94, f"Mean ρ = {rs['spearman_rho'].mean():.2f}",
        transform=ax.transAxes, va="top"
    )
    finish(ax, args.output / "fig4_persistence.png")

    # Fig. 5 — external cross-scale validation.
    fig, ax = plt.subplots(figsize=(5.3, 4.8))
    for borough, g in vp.groupby("borough"):
        ax.scatter(
            100 * g["availability"], 100 * g["asset_reported"],
            s=21, alpha=0.66, label=borough
        )
    mn = min((100 * vp["availability"]).min(), (100 * vp["asset_reported"]).min())
    mx = max((100 * vp["availability"]).max(), (100 * vp["asset_reported"]).max())
    ax.plot([mn, mx], [mn, mx], "--", linewidth=1.0, label="1:1")
    ax.set_xlabel("Accessible-platform availability (%)")
    ax.set_ylabel("Aggregated elevator availability (%)")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    rho, _ = spearmanr(vp["asset_reported"], vp["availability"])
    ax.text(0.03, 0.04, f"Spearman ρ = {rho:.2f}", transform=ax.transAxes)
    finish(ax, args.output / "fig5_validation.png")

    # Supplementary descriptive governance trend.
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    for manager, g in ym.groupby("Managed By"):
        ax.plot(
            g["year"], 100 * g["reported_availability"],
            marker="o", label=manager
        )
    ax.set_xlabel("Year")
    ax.set_ylabel("Reported availability (%)")
    ax.legend(frameon=False, loc="lower left")
    ax.set_xticks(sorted(ym["year"].unique()))
    ax.tick_params(axis="x", rotation=45)
    finish(ax, args.output / "figS1_management_availability.png")

    # Supplementary borough heterogeneity in the denominator gap.
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    for borough, g in yb.groupby("Borough"):
        ax.plot(g["year"], g["metric_gap_pp"], marker="o", label=borough)
    ax.set_xlabel("Year")
    ax.set_ylabel("Availability-continuity gap (pp)")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.set_xticks(sorted(yb["year"].unique()))
    ax.tick_params(axis="x", rotation=45)
    finish(ax, args.output / "figS2_borough_metric_gap.png")


if __name__ == "__main__":
    main()
