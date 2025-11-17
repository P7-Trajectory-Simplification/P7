import math
import unittest

from algorithms.uniform_sampling import run_uniform_sampling, UniformSampling
from classes.route import Route
from tests.test_mock_vessel_logs import mock_vessel_logs
from tests.algorithms.routes_basic_assertions import BasicAssertions

class UniformSamplingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def assumed_number_of_points(self, r: int) -> int:
        n = len(self.route.trajectory)
        if math.fmod(n, r) == 0:
            return int (n - n / r)
        else:
            return n - math.ceil(n / r) + 1

    def test_run_uniform_sampling(self):
        sampling_rate = 10
        simplified_route = run_uniform_sampling(self.route, {"sampling_rate": sampling_rate})

        BasicAssertions(self.route, simplified_route)

    def test_uniform_sampling(self):
        for s in [3, 5, 10, 20, 50]:
            us = UniformSampling(s)
            for vessel_log in self.route.trajectory:
                us.append_point(vessel_log)
                us.simplify()

        self.assertEqual(
            len(us.trajectory),
            self.assumed_number_of_points(s),
            "Simplified route should have correct number of points"
        )


if __name__ == '__main__':
    unittest.main()
