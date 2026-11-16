import unittest

import numpy as np
import pandas as pd

from src.longitudinal_analysis import chronicity


class ChronicityMissingValueTests(unittest.TestCase):
    def test_missing_reported_month_is_not_counted_as_non_low(self):
        months = pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"])
        rows = []
        # Complex 1 has one month with zero reported denominator / missing reported availability.
        rep1 = [0.90, np.nan, 0.80, 0.70]
        cal1 = [0.90, 0.00, 0.80, 0.70]
        for month, rep, cal in zip(months, rep1, cal1):
            rows.append({
                "Month": month,
                "Station Complex MRN": 1,
                "Station Complex Name": "A",
                "Borough": "X",
                "reported_availability": rep,
                "calendar_continuity": cal,
                "excluded_share": 0.0,
                "third_party_share": 0.0,
            })

        # Add three comparison complexes so monthly percentile ranks are defined.
        for cid, vals in {
            2: [0.95, 0.95, 0.95, 0.95],
            3: [0.85, 0.85, 0.85, 0.85],
            4: [0.75, 0.75, 0.75, 0.75],
        }.items():
            for month, val in zip(months, vals):
                rows.append({
                    "Month": month,
                    "Station Complex MRN": cid,
                    "Station Complex Name": str(cid),
                    "Borough": "X",
                    "reported_availability": val,
                    "calendar_continuity": val,
                    "excluded_share": 0.0,
                    "third_party_share": 0.0,
                })

        cm = pd.DataFrame(rows)
        out = chronicity(cm, min_months=1, quantile=0.25)
        a = out.loc[out["Station Complex MRN"] == 1].iloc[0]

        self.assertEqual(int(a["n_months"]), 4)
        self.assertEqual(int(a["n_reported_valid"]), 3)
        self.assertEqual(int(a["n_continuity_valid"]), 4)
        # The missing reported month must be excluded from the recurrence denominator.
        self.assertFalse(np.isnan(a["reported_bq_share"]))

    def test_all_missing_reported_values_remain_missing(self):
        months = pd.to_datetime(["2024-01-01", "2024-02-01"])
        rows = []
        for month in months:
            rows.append({
                "Month": month,
                "Station Complex MRN": 1,
                "Station Complex Name": "A",
                "Borough": "X",
                "reported_availability": np.nan,
                "calendar_continuity": 0.0,
                "excluded_share": 1.0,
                "third_party_share": 0.0,
            })
            rows.append({
                "Month": month,
                "Station Complex MRN": 2,
                "Station Complex Name": "B",
                "Borough": "X",
                "reported_availability": 0.9,
                "calendar_continuity": 0.9,
                "excluded_share": 0.0,
                "third_party_share": 0.0,
            })

        out = chronicity(pd.DataFrame(rows), min_months=1, quantile=0.25)
        a = out.loc[out["Station Complex MRN"] == 1].iloc[0]
        self.assertEqual(int(a["n_reported_valid"]), 0)
        self.assertTrue(np.isnan(a["reported_bq_share"]))


if __name__ == "__main__":
    unittest.main()
