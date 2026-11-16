"""Audit official MTA equipment-by-month availability data.

Usage: python -m src.audit --input data/raw.csv --output outputs
Download first: https://data.ny.gov/api/views/rc78-7x78/rows.csv?accessType=DOWNLOAD
"""
import argparse
import json
from pathlib import Path

import pandas as pd

REQUIRED = ['Month', 'Equipment Code', 'Equipment Type', 'Station Name', '24-Hour Availability']
OPTIONAL = ['Borough', 'Station MRN', 'Station Complex Name', 'Station Complex MRN',
            'Total Outages', 'Scheduled Outages', 'Unscheduled Outages',
            'Entrapments', 'Time Since Major Improvement', 'AM Peak Availability', 'PM Peak Availability']


def availability(s):
    """Return fraction 0..1; supports '98.2%' and numeric 0.982.

    Bare numbers greater than 1 are rejected to avoid silently mixing scales.
    """
    x = s.astype(str).str.strip()
    pct = x.str.contains('%', regex=False)
    v = pd.to_numeric(x.str.replace('%', '', regex=False), errors='coerce')
    v.loc[pct] = v.loc[pct] / 100
    if (~pct & (v > 1)).any():
        raise ValueError('Ambiguous availability scale in non-% values; inspect source dictionary.')
    return v


def audit_frame(raw):
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError(f'Missing required fields: {missing}; columns={list(raw.columns)}')
    d = raw.copy()
    d['Month'] = pd.to_datetime(d['Month'], errors='coerce')
    d['availability'] = availability(d['24-Hour Availability'])
    d['is_elevator'] = d['Equipment Type'].astype(str).str.strip().str.lower().eq('elevator')
    e = d.loc[d['is_elevator']].copy()
    key = ['Equipment Code', 'Month']
    summary = {
        'raw_rows': len(d), 'elevator_rows': len(e),
        'first_month': str(e['Month'].min().date()) if e['Month'].notna().any() else None,
        'last_month': str(e['Month'].max().date()) if e['Month'].notna().any() else None,
        'n_elevator_ids': int(e['Equipment Code'].nunique()),
        'n_station_names': int(e['Station Name'].nunique()),
        'missing_month': int(e['Month'].isna().sum()),
        'missing_availability': int(e['availability'].isna().sum()),
        'invalid_availability': int(((e['availability'] < 0) | (e['availability'] > 1)).sum()),
        'duplicate_equipment_month': int(e.duplicated(key).sum()),
        'optional_columns_present': [c for c in OPTIONAL if c in d.columns],
    }
    if summary['invalid_availability'] or summary['duplicate_equipment_month'] or summary['missing_month']:
        raise ValueError(f'Failed audit: {summary}')
    e['unavailable_share'] = 1 - e['availability']
    return e, summary


def station_month_proxy(e):
    """Asset-only diagnostic; NOT station-accessibility or passenger-journey uptime."""
    keys = ['Station Complex MRN', 'Month'] if 'Station Complex MRN' in e else ['Station Name', 'Month']
    return e.groupby(keys, dropna=False).agg(
        n_elevators=('Equipment Code', 'nunique'),
        mean_asset_availability=('availability', 'mean'),
        minimum_asset_availability=('availability', 'min')
    ).reset_index()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--output', default='outputs')
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(args.input, low_memory=False)
    e, stats = audit_frame(data)
    (out / 'audit.json').write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding='utf-8')
    e.to_csv(out / 'elevators_clean.csv', index=False)
    station_month_proxy(e).to_csv(out / 'station_month_diagnostic.csv', index=False)
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
