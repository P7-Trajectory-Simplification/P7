import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.dp import run_dp, DouglasPeucker


class DouglasPeuckerTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_dp(self):
        simplified_route = run_dp(self.route, {"epsilon": 6000})

        BasicAssertions(self.route, simplified_route)

    def test_douglas_peucker(self):
        dp = DouglasPeucker(epsilon=6000)
        for vessel_log in self.route.trajectory:
            dp.append_point(vessel_log)
            dp.simplify()

        BasicAssertions(self.route, Route(dp.trajectory))

if __name__ == '__main__':
    unittest.main()
