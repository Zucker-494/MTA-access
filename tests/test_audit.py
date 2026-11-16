import unittest

import pandas as pd
from src.audit import audit_frame, station_month_proxy


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.d = pd.DataFrame({
            'Month': ['2024-01-01', '2024-01-01', '2024-02-01'],
            'Equipment Code': ['EL01', 'EL02', 'EL01'],
            'Equipment Type': ['Elevator'] * 3,
            'Station Name': ['Alpha'] * 3,
            '24-Hour Availability': ['98%', '91.5%', '99%'],
            'Station Complex MRN': ['C1'] * 3,
        })

    def test_percent_and_counts(self):
        e, stats = audit_frame(self.d)
        self.assertEqual(stats['elevator_rows'], 3)
        self.assertAlmostEqual(e.iloc[0].availability, 0.98)
        self.assertEqual(len(station_month_proxy(e)), 2)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            audit_frame(pd.concat([self.d, self.d.iloc[[0]]], ignore_index=True))

    def test_invalid_scale_rejected(self):
        d = self.d.copy()
        d.loc[0, '24-Hour Availability'] = '98'
        with self.assertRaises(ValueError):
            audit_frame(d)


if __name__ == '__main__':
    unittest.main()
