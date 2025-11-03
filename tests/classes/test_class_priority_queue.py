import unittest

from classes.priority_queue import PriorityQueue
from tests.test_mock_vessel_logs import mock_vessel_logs

class RouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.heap = PriorityQueue()

    def test_priority_queue(self):
        for i, log in enumerate(mock_vessel_logs):
            self.heap.insert(i, log, priority=i*10)

        self.assertEqual(len(self.heap.entry_finder), len(mock_vessel_logs), "Heap size should match number of inserted logs")
        self.assertEqual(self.heap.min_priority(), 0, "Minimum priority should be 0")

        self.heap.remove_min()
        self.assertEqual(self.heap.min_priority(), 10, "Minimum priority should be 10 after removing min")

        self.heap.remove(1)
        self.assertNotIn(1, self.heap.entry_finder, "Log with point_id 1 should be removed from entry_finder")

        self.heap.update_priority(2, 5)
        self.assertEqual(self.heap.min_priority(), 5, "Minimum priority should be updated to 5 after priority update")

        priority = self.heap.min_priority()
        self.assertEqual(priority, 5, "Minimum priority should be 5")

if __name__ == '__main__':
    unittest.main()
