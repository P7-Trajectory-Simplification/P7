import math
import unittest

from algorithms.uniform_sampling import run_uniform_sampling, uniform_sampling
from classes.route import Route
from tests.test_mock_vessel_logs import mock_vessel_logs
from tests.algorithms.routes_basic_assertions import BasicAssertions

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

        BasicAssertions(self.route, simplified_route)

        self.assertEqual(
            len(simplified_route.trajectory),
            self.assumed_number_of_points(sampling_rate),
            "Simplified route should have correct number of points"
        )

    def test_uniform_sampling(self):
        uniform_sampling(self.route.trajectory, sampling_rate=100)


if __name__ == '__main__':
    unittest.main()
