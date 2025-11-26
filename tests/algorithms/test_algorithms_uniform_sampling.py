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
            return int(n / r)
        else:
            return n - math.ceil(n / r) + 1

    def test_run_uniform_sampling(self):
        sampling_rate = 10
        simplified_route = run_uniform_sampling(
            self.route, {"sampling_rate": sampling_rate}
        )

        BasicAssertions(self.route, simplified_route)

        # Compute expected number of points according to uniform_sampling logic
        n = len(self.route.trajectory)
        if n <= 2:
            expected_len = n
        else:
            # First and last are always kept
            # Middle points removed every time counter < sampling_rate
            # Roughly, keep ceil(n / sampling_rate) points
            num_full_cycles = n // sampling_rate
            remainder = n % sampling_rate
            expected_len = 2 + num_full_cycles + (1 if remainder > 0 else 0)

        simplified_len = len(simplified_route.trajectory)

        self.assertEqual(
            simplified_len,
            expected_len,
            f"Simplified route should have {expected_len} points, got {simplified_len}",
        )


if __name__ == "__main__":
    unittest.main()
