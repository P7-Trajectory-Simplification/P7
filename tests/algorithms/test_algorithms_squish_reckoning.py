import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish_reckoning import run_sr, SquishReckoning

class SquishReckoningTest (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def setUp(self):
        # Clear memoized scores before each test to avoid interference
        self.route = Route(trajectory=mock_vessel_logs.copy())

    def test_run_squish_reckoning(self):
        self.route = Route(trajectory=mock_vessel_logs)
        simplified_route = run_sr(self.route, {"buff_size": 100})

        BasicAssertions(self.route, simplified_route)
    
    def test_squish_reckoning(self):
        squishReckoning = SquishReckoning(len(self.route.trajectory) + 5)
        for vessel_log in self.route.trajectory:
           squishReckoning.trajectory.append(vessel_log)
           squishReckoning.simplify()

        self.assertEqual(len(squishReckoning.trajectory), len(self.route.trajectory), "No points should be removed when below buffer size.")

        squishReckoning = SquishReckoning(5)
        for vessel_log in self.route.trajectory:
            squishReckoning.trajectory.append(vessel_log)
            squishReckoning.simplify()

        self.assertLessEqual(len(squishReckoning.trajectory), 5, "Trajectory should not exceed buffer size after squishing.")

if __name__ == '__main__':
    unittest.main()
