import unittest
import numpy as np
from tests.test_mock_vessel_logs import mock_vessel_logs, mock_vessel_logs_second_route

from error_metrics.ped import (
    find_nearest_simplified_idx_vectorized, 
    ped_single_route_vectorized, 
    ped_results,)

class PedTest(unittest.TestCase):
    # Tests: find_nearest_simplified_idx_vectorized
    def test_find_nearest_basic(self):
        raw = np.array([10, 20, 30])
        simp = np.array([0, 15, 25, 35])

        left, right = find_nearest_simplified_idx_vectorized(raw, simp)

        self.assertTrue(np.array_equal(left, np.array([0, 1, 2])),
                        "Left indices should match nearest simplified positions.")
        self.assertTrue(np.array_equal(right, np.array([1, 2, 3])),
                        "Right indices should match nearest simplified positions.")

    def test_find_nearest_clamping(self):
        raw = np.array([1, 2, 3])
        simp = np.array([10, 20, 30])

        left, right = find_nearest_simplified_idx_vectorized(raw, simp)

        self.assertTrue(np.all(left == 0), "Left indices should clamp to 0.")
        self.assertTrue(np.all(right == 1), "Right indices should clamp to 1.")

    # Tests: ped_single_route_vectorized
    def test_ped_single_empty(self):
        avg, maxd, count = ped_single_route_vectorized([], [])
        self.assertEqual(avg, 0, "Empty input should yield average of 0.")
        self.assertEqual(maxd, 0, "Empty input should yield max of 0.")
        self.assertEqual(count, 0, "Empty input should result in count 0.")

    def test_ped_single_one_simplified_point(self):
        raw = mock_vessel_logs
        simp = [mock_vessel_logs[0]]  # only first point

        avg, maxd, count = ped_single_route_vectorized(raw, simp)

        self.assertEqual(count, len(raw), "Count should equal number of raw points.")
        self.assertGreaterEqual(avg, 0, "Average PED must be non-negative.")
        self.assertGreaterEqual(maxd, 0, "Max PED must be non-negative.")
        self.assertGreaterEqual(maxd, avg, "Max PED should be >= average PED.")

    def test_ped_single_normal(self):
        raw = mock_vessel_logs
        simp = [mock_vessel_logs[0], mock_vessel_logs[-1]]

        avg, maxd, count = ped_single_route_vectorized(raw, simp)

        self.assertEqual(count, len(raw), "All raw points should be evaluated.")
        self.assertGreaterEqual(avg, 0)
        self.assertGreaterEqual(maxd, avg)

    # Tests: ped_results
    def test_ped_results_empty(self):
        avg, maxd = ped_results({}, {})
        self.assertEqual(avg, 0.0, "Empty route data should produce avg=0.")
        self.assertEqual(maxd, 0.0, "Empty route data should produce max=0.")

    def test_ped_results_single_route(self):
        raw = mock_vessel_logs
        simp = [mock_vessel_logs[0], mock_vessel_logs[-1]]

        avg, maxd = ped_results(
            {1: raw},
            {1: simp}
        )

        self.assertGreaterEqual(avg, 0)
        self.assertGreaterEqual(maxd, avg)

    def test_ped_results_multiple_routes(self):
        raw_routes = {
            1: mock_vessel_logs,
            2: mock_vessel_logs_second_route,
        }
        simplified_routes = {
            1: [raw_routes[1][0], raw_routes[1][-1]],
            2: [raw_routes[2][0], raw_routes[2][-1]],
        }

        avg, maxd = ped_results(raw_routes, simplified_routes)

        self.assertGreaterEqual(avg, 0, "Average PED across routes should be non-negative.")
        self.assertGreaterEqual(maxd, avg, "Maximum PED should be >= average PED.")


if __name__ == '__main__':
    unittest.main()