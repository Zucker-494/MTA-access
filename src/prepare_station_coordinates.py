"""Create the frozen station-complex coordinate snapshot from official MTA data."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    d = pd.read_csv(args.input)
    lower = {c.lower().strip().replace(" ", "_"): c for c in d.columns}

    required = ["complex_id", "stop_name", "borough", "latitude", "longitude"]
    missing = [c for c in required if c not in lower]
    if missing:
        raise ValueError(f"Official station file missing fields: {missing}")

    out = pd.DataFrame({
        "complex_id": pd.to_numeric(d[lower["complex_id"]], errors="coerce"),
        "station_name": d[lower["stop_name"]].astype(str),
        "borough": d[lower["borough"]].astype(str),
        "latitude": pd.to_numeric(d[lower["latitude"]], errors="coerce"),
        "longitude": pd.to_numeric(d[lower["longitude"]], errors="coerce"),
    }).dropna(subset=["complex_id", "latitude", "longitude"])

    out = out.sort_values("complex_id").drop_duplicates("complex_id", keep="first")
    out["complex_id"] = out["complex_id"].astype(int)

    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(target, index=False)
    print(f"Wrote {len(out)} station complexes to {target}")


if __name__ == "__main__":
    main()
