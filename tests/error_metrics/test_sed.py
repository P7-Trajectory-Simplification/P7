import unittest
import numpy as np
from datetime import datetime, timedelta
from tests.test_mock_vessel_logs import mock_vessel_logs

from classes.vessel_log import VesselLog
from error_metrics.sed import (
    interpolate_simplified_points_vectorized,
    slerp,
    sed_single_route_vectorized,
    sed_results,
)

class SedTest(unittest.TestCase):
    def test_interpolate_simplified_points_vectorized(self):
        """Tests that the interpolated points fall between the simplified timestamps."""
        raw_times = np.array([5, 10, 15])
        simp_times = np.array([0, 20])
        simp_latlon = np.array([[0.0, 0.0],[0.0, np.radians(90)]])

        result = interpolate_simplified_points_vectorized(raw_times, simp_times, simp_latlon)

        # The points should interpolate toward longitude 90° gradually
        self.assertEqual(result.shape, (3, 2))
        self.assertTrue(result[0][1] < result[1][1] < result[2][1],
                        "Longitudes should increase monotonically for uniform interpolation.")
        

    def test_slerp_identical_points(self):
        """If the points are identical, SLERP should return the same point."""
        p = np.array([np.radians(10), np.radians(20)])
        result = slerp(p, p, 0.5)
        self.assertTrue(np.allclose(result, p), "SLERP of identical points must return the point.")

    def test_slerp_midpoint(self):
        """Midpoint between two known positions should be on the great circle arc."""
        p0 = np.array([np.radians(0), np.radians(0)])
        p1 = np.array([np.radians(0), np.radians(90)])
        mid = slerp(p0, p1, 0.5)

        # expect latitude ~0, longitude ~45°
        self.assertAlmostEqual(mid[0], 0, places=5)
        self.assertAlmostEqual(np.degrees(mid[1]), 45.0, places=2)

    
    def test_sed_single_empty(self):
        """Tests SED calculation on empty input."""
        avg, maxd, count = sed_single_route_vectorized([], [])
        self.assertEqual(avg, 0)
        self.assertEqual(maxd, 0)
        self.assertEqual(count, 0)

    def test_sed_single_one_simplified_point(self):
        """Tests SED calculation when only one simplified point is provided."""
        raw = mock_vessel_logs
        simp = [mock_vessel_logs[0]]  # only first point

        avg, maxd, count = sed_single_route_vectorized(raw, simp)

        self.assertEqual(count, len(raw))
        self.assertGreaterEqual(avg, 0)
        self.assertGreaterEqual(maxd, 0)
        self.assertGreaterEqual(maxd, avg)

    def test_sed_single_normal(self):
        """Tests SED calculation on a normal case with multiple simplified points."""
        raw = mock_vessel_logs
        simp = [raw[0], raw[-1]]

        avg, maxd, count = sed_single_route_vectorized(raw, simp)

        self.assertEqual(count, len(raw))
        self.assertGreaterEqual(avg, 0)
        self.assertGreaterEqual(maxd, avg)


    def test_sed_results_empty(self):
        """Tests SED results calculation on empty input."""
        avg, maxd = sed_results({}, {})
        self.assertEqual(avg, 0.0)
        self.assertEqual(maxd, 0.0)

    def test_sed_results_single_route(self):
        """Tests SED results calculation on a single route."""
        raw = mock_vessel_logs
        simp = [raw[0], raw[-1]]

        avg, maxd = sed_results({1: raw}, {1: simp})

        self.assertGreaterEqual(avg, 0)
        self.assertGreaterEqual(maxd, avg)

    def test_sed_results_multiple_routes(self):
        """Tests SED results calculation on multiple routes."""
        raw_routes = {1: mock_vessel_logs, 2: mock_vessel_logs}
        simp_routes = {
            1: [raw_routes[1][0], raw_routes[1][-1]],
            2: [raw_routes[2][0], raw_routes[2][-1]],
        }

        avg, maxd = sed_results(raw_routes, simp_routes)

        self.assertGreaterEqual(avg, 0)
        self.assertGreaterEqual(maxd, avg)


if __name__ == "__main__":
    unittest.main()

        