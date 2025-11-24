import unittest
from tests.test_mock_vessel_logs import mock_vessel_logs, mock_vessel_logs_second_route

from error_metrics.comp_ratio import comp_ratio_results

class TestCompressionRatio(unittest.TestCase):

    def test_single_route_half_reduction(self):
        """
        Simplify to half the number of points.
        """
        raw = {1: mock_vessel_logs}
        simplified = {1: mock_vessel_logs[:len(mock_vessel_logs)//2]} # Array slicing to half

        expected_ratio = len(mock_vessel_logs) // 2 / len(mock_vessel_logs)

        result = comp_ratio_results(raw, simplified)
        self.assertEqual(result, round(expected_ratio, 4))

    def test_two_routes_mixed_reduction(self):
        """
        Test two routes with different simplification levels.
        """
        raw = {
            1: mock_vessel_logs,
            2: mock_vessel_logs_second_route,
        }

        simplified = {
            1: mock_vessel_logs[:10],                 # 50 → 10
            2: mock_vessel_logs_second_route[:25],    # 50 → 25
        }

        total_raw = len(mock_vessel_logs) + len(mock_vessel_logs_second_route)
        total_simplified = 10 + 25

        expected_ratio = total_simplified / total_raw

        result = comp_ratio_results(raw, simplified)
        self.assertEqual(result, round(expected_ratio, 4))

    def test_zero_simplified_points(self):
        raw = {1: mock_vessel_logs}
        simplified = {1: []}

        result = comp_ratio_results(raw, simplified)
        self.assertEqual(result, 0.0)

    def test_zero_raw_points(self):
        raw = {1: []}
        simplified = {1: mock_vessel_logs}

        # total_raw_points == 0 → return 0.0
        result = comp_ratio_results(raw, simplified)
        self.assertEqual(result, 0.0)

    def test_identical_route(self):
        raw = {1: mock_vessel_logs}
        simplified = {1: mock_vessel_logs}

        result = comp_ratio_results(raw, simplified)
        self.assertEqual(result, 1.0)

    def test_missing_key_in_simplified(self):
        raw = {1: mock_vessel_logs}
        simplified = {}  # missing key 1

        with self.assertRaises(KeyError):
            comp_ratio_results(raw, simplified)


if __name__ == "__main__":
    unittest.main()
