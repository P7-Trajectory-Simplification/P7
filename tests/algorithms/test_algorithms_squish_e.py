import unittest

from classes.route import Route
from tests.algorithms.routes_basic_assertions import BasicAssertions
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish_e import run_squish_e, squish_e, adjust_priority, reduce
from classes.priority_queue import PriorityQueue


class SquishETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_squish_e(self):
        self.route = Route(trajectory=mock_vessel_logs)
        squished_e_route = run_squish_e(self.route, {"low_comp": 2, "max_sed": 100})

        BasicAssertions(self.route, squished_e_route)

    def test_squish_e(self):
        for low_comp_rate in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            self.route = Route(trajectory=mock_vessel_logs)
            squish_e(self.route.trajectory, self.route.squish_e_buff, low_comp_rate=low_comp_rate, up_bound_sed=0)

            self.assertEqual(len(self.route.trajectory)/len(self.route.squish_e_buff) >= low_comp_rate, True, "Compression rate should fulfill the equation")

            BasicAssertions(self.route, Route(self.route.squish_e_buff))

    def test_adjust_priority(self):
        self.route = Route(trajectory=mock_vessel_logs)
        heap = PriorityQueue()
        pred = {}
        succ = {}
        max_neighbor = {}

        heap.insert(0, self.route.trajectory[0])
        max_neighbor[0] = 0

        heap.insert(1, self.route.trajectory[1])
        max_neighbor[1] = 0
        succ[0] = 1
        pred[1] = 0

        heap.insert(2, self.route.trajectory[2])
        max_neighbor[2] = 0
        succ[1] = 2
        pred[2] = 1


        adjust_priority(0, self.route.trajectory[0], self.route.trajectory, heap, pred, succ, max_neighbor)
        adjust_priority(1, self.route.trajectory[1], self.route.trajectory, heap, pred, succ, max_neighbor)
        adjust_priority(2, self.route.trajectory[2], self.route.trajectory, heap, pred, succ, max_neighbor)

        self.assertEqual(heap.entry_finder[0][0], float('inf'), "Priority of point 0 should not be updated")
        self.assertNotEqual(heap.entry_finder[1][0], float('inf'), "Priority of point 1 should be updated")
        self.assertEqual(heap.entry_finder[2][0], float('inf'), "Priority of point 2 should not be updated")


    def test_reduce(self):
        self.route = Route(trajectory=mock_vessel_logs)

if __name__ == '__main__':
    unittest.main()
