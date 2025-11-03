
import unittest

from datetime import datetime, timedelta

import numpy as np
from classes.route import Route
from classes.vessel_log import VesselLog
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.dead_reckoning import run_dr, dead_reckoning, reckon

class DeadReckoningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)
    
    def test_run_dr(self):
        simplified_route = run_dr(self.route, {"tolerance": 2000})
        
        self.assertLess(len(simplified_route.trajectory), len(self.route.trajectory), "Simplified route should have fewer points")
        self.assertEqual(simplified_route.trajectory[0], self.route.trajectory[0], "First point should remain the same")
        self.assertEqual(simplified_route.trajectory[-1], self.route.trajectory[-1], "Last point should remain the same")

        original = {p.get_coords() for p in self.route.trajectory}
        simplified = {p.get_coords() for p in simplified_route.trajectory}
        self.assertTrue(simplified.issubset(original), "Simplified trajectory must contain only original points.")

    def test_dead_reckoning(self):
        base_lat, base_lon = 55.0, 12.0
        t0 = datetime(2024, 1, 1, 12, 0, 0)

        a = VesselLog(lat=base_lat, lon=base_lon, ts=t0)
        b = VesselLog(lat=base_lat + (1_000 / 111_000), lon=base_lon, ts=t0 + timedelta(seconds=60))
        # C is ~6 km east of the expected path.
        c = VesselLog(lat=base_lat + (2_000 / 111_000), lon=base_lon + (6_000 / (111_000 * np.cos(np.deg2rad(base_lat)))), ts=t0 + timedelta(seconds=120))

        simplified = []
        trajectory = [a,b,c]
        for point in trajectory:
            simplified.append(point)
            simplified = dead_reckoning(simplified, 2000)
        self.assertEqual(len(simplified), 3, "Trajectory should not drop any point since error > tolerance")


        # Point C — close to expected path
        c = VesselLog(
            lat=base_lat + (2_000 / 111_000),
            lon=base_lon + (10 / (111_000 * np.cos(np.deg2rad(base_lat)))),  # ~10 m east
            ts=t0 + timedelta(seconds=120)
        )
        trajectory = [a,b,c]
        simplified = []
        for point in trajectory:
            simplified.append(point)
            simplified = dead_reckoning(simplified, 2000)
        self.assertEqual(len(simplified), 2, "Trajectory should drop the middle point, since error < tolerance")
        self.assertEqual(trajectory[0], simplified[0])
        self.assertEqual(trajectory[-1], simplified[-1])
    
    def test_reckon(self):
        base_lat, base_lon = 0.0, 0.0
        t0 = datetime(2024, 1, 1, 12, 0, 0)

        a = VesselLog(lat=base_lat, lon=base_lon, ts=t0)
        b = VesselLog(lat=base_lat, lon=base_lon + (1_000 / (111_000 * 1)), ts=t0 + timedelta(seconds=60))
        # Predicted C (if continuing straight east) would be 2 km east of A
        # We move it 2 km east + 100 m north
        c = VesselLog(
            lat=base_lat + (100 / 111_000),                      # 100 m north deviation
            lon=base_lon + (2_000 / 111_000),                    # 2 km east
            ts=t0 + timedelta(seconds=120)
        )

        result = reckon(a,b,c)
        expected_error = 100

        self.assertAlmostEqual(
            result, expected_error, delta=5.0,
            msg=f"Expected ~{expected_error:.1f}m, got {result:.2f}m"
        )
    

if __name__ == '__main__':
    unittest.main()