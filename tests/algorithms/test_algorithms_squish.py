import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish import run_squish, squish


class SquishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_squish(self):
        squished_route = run_squish(self.route, {"buff_size": 10})

        BasicAssertions(self.route, squished_route)

    def test_squish(self):
        self.route = Route(trajectory=mock_vessel_logs)
        squish(self.route.trajectory, self.route.squish_buff, buff_size=10)
        self.assertEqual(len(self.route.squish_buff), 10, "Squished route should have 10 points")

    #def test_update_sed(self):


if __name__ == '__main__':
    unittest.main()
