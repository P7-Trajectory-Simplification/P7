import unittest

from classes.route import Route
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.dp import run_dp, douglas_peucker


class DouglasPeuckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_dp(self):
        simplified_route = run_dp(self.route, {"epsilon": 6000})

        self.assertLess(len(simplified_route.trajectory), len(self.route.trajectory), "Simplified route should have fewer points")
        self.assertEqual(simplified_route.trajectory[0], self.route.trajectory[0], "First point should remain the same")
        self.assertEqual(simplified_route.trajectory[-1], self.route.trajectory[-1], "Last point should remain the same")

    def test_douglas_peucker(self):
        simplified_trajectory = douglas_peucker(self.route.trajectory, epsilon=6000)

        self.assertLess(len(simplified_trajectory), len(self.route.trajectory), "Douglas-Peucker should reduce number of points")
        self.assertEqual(simplified_trajectory[0], self.route.trajectory[0], "First point should remain the same")
        self.assertEqual(simplified_trajectory[-1], self.route.trajectory[-1], "Last point should remain the same")


if __name__ == '__main__':
    unittest.main()
