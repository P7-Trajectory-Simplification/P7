import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish import run_squish, Squish


class SquishTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_squish(self):
        squished_route = run_squish(self.route, {"buff_size": 10})

        BasicAssertions(self.route, squished_route)

    def test_Squish(self):
        squish_alg = Squish(buffer_size=10)

        for vessel_log in self.route.trajectory:
            squish_alg.trajectory.append(vessel_log)
            squish_alg.simplify()

        self.assertEqual(10, len(squish_alg.trajectory), "Squished route should have 10 points")

    #def test_update_sed(self):


if __name__ == '__main__':
    unittest.main()
