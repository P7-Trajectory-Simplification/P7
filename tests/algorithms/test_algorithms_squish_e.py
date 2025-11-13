import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish_e import run_squish_e, SquishE


class SquishETest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_squish_e(self):
        self.route = Route(trajectory=mock_vessel_logs)
        squished_e_route = run_squish_e(self.route, {"low_comp": 2, "max_sed": 100})

        BasicAssertions(self.route, squished_e_route)

    def test_SquishE(self):
        squish_e_alg = SquishE(lower_compression_rate=2, upper_bound_sed=100)

        for vessel_log in self.route.trajectory:
            squish_e_alg.trajectory.append(vessel_log)
            squish_e_alg.simplify()

        self.assertEqual(len(squish_e_alg.trajectory) <= len(self.route.trajectory)/2, True, "Squished route should have at most 1/2 of the original points")

    def test_squish_e(self):
        for low_comp_rate in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            squish_e_alg = SquishE(lower_compression_rate=low_comp_rate, upper_bound_sed=0)
            for vessel_log in self.route.trajectory:
                squish_e_alg.trajectory.append(vessel_log)
                squish_e_alg.simplify()

            self.assertEqual(len(self.route.trajectory)/len(squish_e_alg.trajectory) >= low_comp_rate, True, "Compression rate should fulfill the equation")

            BasicAssertions(self.route, Route(squish_e_alg.trajectory))

    def test_adjust_priority(self):
        squishE = SquishE(lower_compression_rate=2, upper_bound_sed=0)

        p1 = self.route.trajectory[0]
        p2 = self.route.trajectory[1]
        p3 = self.route.trajectory[2]

        squishE.buffer.insert(p1)
        squishE.buffer.insert(p2)
        squishE.buffer.insert(p3)

        squishE.max_neighbor[p1.id] = 0
        squishE.max_neighbor[p2.id] = 0
        squishE.max_neighbor[p3.id] = 0

        squishE.buffer.succ[p1.id] = p2
        squishE.buffer.pred[p2.id] = p1

        squishE.buffer.succ[p2.id] = p3
        squishE.buffer.pred[p3.id] = p2

        squishE.adjust_priority(p1)
        squishE.adjust_priority(p2)
        squishE.adjust_priority(p3)

        self.assertEqual(squishE.buffer.entry_finder[p1.id][0], float('inf'), "Priority of point 0 should not be updated")
        self.assertNotEqual(squishE.buffer.entry_finder[p2.id][0], float('inf'), "Priority of point 1 should be updated")
        self.assertEqual(squishE.buffer.entry_finder[p3.id][0], float('inf'), "Priority of point 2 should not be updated")

if __name__ == '__main__':
    unittest.main()
