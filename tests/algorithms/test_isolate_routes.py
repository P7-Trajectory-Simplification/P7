import unittest
from datetime import datetime, timedelta

from classes.route import Route
from classes.vessel_log import VesselLog
from algorithms.isolate_routes import isolate_routes


class IsolateRoutesTest(unittest.TestCase):
    def test_isolate_routes(self):
        # Isolate empty trajectory data
        empty_result = isolate_routes([])
        self.assertEqual(len(empty_result), 1, "Should return a list with one empty Route for empty input.")
        self.assertIsInstance(empty_result[0], Route, "Returned object should be a Route instance.")
        self.assertEqual(len(empty_result[0].trajectory), 0, "Empty Route should contain no points.")

        # Mock data with time gap bigger than 2 days (Should maybe be a parameter in the isolate routes function)
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        logs = [
            VesselLog(ts=start_time, lon=10, lat=50),
            VesselLog(ts=start_time + timedelta(hours=1), lon=10.1, lat=50.1),
            VesselLog(ts=start_time + timedelta(days=3), lon=11, lat=51),  # gap > 2 days, should start new route
            VesselLog(ts=start_time + timedelta(days=3, hours=1), lon=11.1, lat=51.1),
        ]

        routes = isolate_routes(logs)

        self.assertEqual(len(routes), 2, "Should split into two routes due to time gap > 2 days.")
        self.assertIsInstance(routes[0], Route)
        self.assertIsInstance(routes[1], Route)

        # Check first route
        self.assertEqual(len(routes[0].trajectory), 2, "First route should have two logs.")
        self.assertEqual(routes[0].trajectory[0], logs[0], "First point should match the first VesselLog.")
        self.assertEqual(routes[0].trajectory[-1], logs[1], "Last point of first route should match.")

        # Check second route
        self.assertEqual(len(routes[1].trajectory), 2, "Second route should have two logs.")
        self.assertEqual(routes[1].trajectory[0], logs[2], "Second route should start at log after time gap.")
        self.assertEqual(routes[1].trajectory[-1], logs[3], "Second route should end with the final log.")

        # All logs are close to each other so isolate_routes shouldnt split them
        close_logs = [
            VesselLog(ts=start_time, lon=12, lat=52),
            VesselLog(ts=start_time + timedelta(hours=12), lon=12.1, lat=52.1),
            VesselLog(ts=start_time + timedelta(days=1, hours=1), lon=12.2, lat=52.2)
        ]
        routes = isolate_routes(close_logs)
        self.assertEqual(len(routes), 1, "All logs within 2 days should form one route.")
        self.assertEqual(len(routes[0].trajectory), len(close_logs), "All logs should be included in one route.")


if __name__ == '__main__':
    unittest.main()
