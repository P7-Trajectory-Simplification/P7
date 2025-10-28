import unittest

from classes.route import Route
from classes.squish_point import SquishPoint
from tests.test_mock_vessel_logs import mock_vessel_logs
from algorithms.squish import run_squish, squish, find_min_sed, update_sed


class SquishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = Route(trajectory=mock_vessel_logs)

    def test_run_squish(self):
        squished_route = run_squish(self.route, {"buff_size": 10})
        self.assertEqual(len(squished_route.trajectory), 10, "Squished route should have 10 points")

    def test_squish(self):
        squish(self.route.trajectory, self.route.squish_buff, buff_size=10)
        squished_route = Route(self.route.extract_squish_buffer())
        self.assertEqual(len(squished_route.trajectory), 10, "Squished route should have 10 points")
        for i, squish_point in enumerate(self.route.squish_buff):
            if i == 0:
                self.assertEqual(squish_point.vessel_log, self.route.trajectory[0], "First point should match")
                self.assertEqual(squish_point.sed, float('inf'), "First point SED should be infinity")
            elif i == len(self.route.squish_buff) - 1:
                self.assertEqual(squish_point.vessel_log, self.route.trajectory[-1], "Last point should match")
                self.assertEqual(squish_point.sed, float('inf'), "Last point SED should be infinity")
            else:
                self.assertNotEqual(squish_point.sed, float('inf'), "Intermediate point SED should be updated")

    def test_find_min_sed(self):
        buff = [
            SquishPoint(self.route.trajectory[0], sed=float(1)),
            SquishPoint(self.route.trajectory[1], sed=float(2)),
            SquishPoint(self.route.trajectory[2], sed=float(3)),
            SquishPoint(self.route.trajectory[3], sed=float(1.9)),
            SquishPoint(self.route.trajectory[4], sed=float(1.5)),
        ]

        min_index = find_min_sed(buff)
        self.assertEqual(min_index, 3, "Minimum SED index should be 3")
        del buff[min_index]
        min_index = find_min_sed(buff)
        self.assertEqual(min_index, 1, "Minimum SED index should be 1")

    def test_update_sed(self):
        buff = [
            SquishPoint(self.route.trajectory[0], sed=float('inf')),
            SquishPoint(self.route.trajectory[1], sed=float('inf')),
            SquishPoint(self.route.trajectory[2], sed=float('inf')),
        ]
        update_sed(1, buff)
        self.assertNotEqual(buff[1].sed, float('inf'), "SED should be updated to less than infinity")

        self.assertRaises(IndexError, update_sed, 0, buff) # Should raise IndexError for first element
        self.assertRaises(IndexError, update_sed, 2, buff) # Should raise IndexError for last element


if __name__ == '__main__':
    unittest.main()
