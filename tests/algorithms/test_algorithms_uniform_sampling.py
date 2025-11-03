import math
import unittest

from algorithms.uniform_sampling import run_uniform_sampling, uniform_sampling
from classes.route import Route
from tests.test_mock_vessel_logs import mock_vessel_logs


class UniformSamplingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def assumed_number_of_points(self, r):
        n = len(self.route.trajectory)
        if math.fmod(n - 1, r) == 0:
            return math.ceil(n / r)
        else:
            return math.ceil(n / r) + 1

    def test_run_uniform_sampling(self):
        sampling_rate = 10
        simplified_route = run_uniform_sampling(self.route, {"sampling_rate": sampling_rate})

        self.assertLessEqual(len(simplified_route.trajectory), len(self.route.trajectory), "Simplified route should have fewer or equal points")
        self.assertEqual(simplified_route.trajectory[0], self.route.trajectory[0], "First point should remain the same")
        self.assertEqual(simplified_route.trajectory[-1], self.route.trajectory[-1], "Last point should remain the same")

        self.assertEqual(
            len(simplified_route.trajectory),
            self.assumed_number_of_points(sampling_rate),
            "Simplified route should have correct number of points"
        )

        original = {p.get_coords() for p in self.route.trajectory}
        simplified = {p.get_coords() for p in simplified_route.trajectory}
        self.assertTrue(simplified.issubset(original), "Simplified trajectory must contain only original points.")

    def test_uniform_sampling(self):
        sampling_rate = 100
        simplified_trajectory = uniform_sampling(self.route.trajectory, sampling_rate=sampling_rate)

        self.assertLessEqual(len(simplified_trajectory), len(self.route.trajectory), "Simplified route should have fewer or equal points")
        self.assertEqual(simplified_trajectory[0], self.route.trajectory[0], "First point should remain the same")
        self.assertEqual(simplified_trajectory[-1], self.route.trajectory[-1], "Last point should remain the same")

        self.assertEqual(
            len(simplified_trajectory),
            self.assumed_number_of_points(sampling_rate),
            "Simplified route should have correct number of points"
        )


if __name__ == '__main__':
    unittest.main()
