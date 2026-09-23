import unittest

from app.report import monthly_total


class ReportTest(unittest.TestCase):
    # Known failure, tracked separately (float rounding in the admin report).
    def test_cents_add_up(self):
        self.assertEqual(monthly_total([0.1, 0.2]), 0.3)


if __name__ == "__main__":
    unittest.main()
