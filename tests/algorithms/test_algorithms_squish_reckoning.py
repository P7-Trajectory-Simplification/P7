import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish_reckoning import run_sr, squish_reckoning, scores

class SquishReckoningTest (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def setUp(self):
        # Clear memoized scores before each test to avoid interference
        scores.clear()
        self.route = Route(trajectory=mock_vessel_logs.copy())

    def test_run_squish_reckoning(self):
        self.route = Route(trajectory=mock_vessel_logs)
        simplified_route = run_sr(self.route, {"buff_size": 100})

        BasicAssertions(self.route, simplified_route)
    
    def test_squish_reckoning(self):
        trajectory_copy = self.route.trajectory.copy()
        simplified_route = []
        for point in trajectory_copy:
            simplified_route.append(point)
            simplified_route = squish_reckoning(simplified_route, buffer_size=len(trajectory_copy) + 5)

        self.assertEqual(len(simplified_route), len(self.route.trajectory), "No points should be removed when below buffer size.")

        small_buffer = 5
        trajectory_copy = self.route.trajectory.copy()
        simplified_route = []
        for point in trajectory_copy:
            simplified_route.append(point)
            simplified_route = squish_reckoning(simplified_route, buffer_size=small_buffer)

        self.assertLessEqual(len(simplified_route), small_buffer, "Trajectory should not exceed buffer size after squishing.")


        self.assertTrue(len(scores) > 0, "Scores dictionary should be populated after reckoning.")

if __name__ == '__main__':
    unittest.main()
