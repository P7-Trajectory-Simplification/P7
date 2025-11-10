import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.dp import run_dp, douglas_peucker


class DouglasPeuckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_dp(self):
        simplified_route = run_dp(self.route, {"epsilon": 6000})

        BasicAssertions(self.route, simplified_route)

    def test_douglas_peucker(self):
        douglas_peucker(self.route.trajectory, epsilon=6000)



if __name__ == '__main__':
    unittest.main()
