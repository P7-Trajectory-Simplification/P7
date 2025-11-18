import unittest

from classes.priority_queue import PriorityQueue
from tests.test_mock_vessel_logs import mock_vessel_logs

class RouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.heap = PriorityQueue()

    def test_priority_queue(self):
        for log in mock_vessel_logs:
            if log != mock_vessel_logs[0] and log != mock_vessel_logs[-1]:
                priority = log.id * 10
            else:
                priority = float('inf')
            self.heap.insert(log, priority)




        self.assertEqual(len(self.heap.entry_finder), len(mock_vessel_logs), "Heap size should match number of inserted logs")
        self.assertEqual(self.heap.min_priority(), mock_vessel_logs[1].id*10, "Minimum priority should be that of the second log")

        self.heap.remove_min()
        self.assertEqual(self.heap.min_priority(), mock_vessel_logs[2].id*10, "Minimum priority should be that of the third log after removing min")

        self.heap.remove(mock_vessel_logs[2])
        self.assertNotIn(mock_vessel_logs[2].id, self.heap.entry_finder, "The fourth log should be removed from entry_finder")

        self.assertEqual(self.heap.min_priority(), mock_vessel_logs[3].id*10, "Minimum priority should be that of the fifth log after removing the fourth")

if __name__ == '__main__':
    unittest.main()
