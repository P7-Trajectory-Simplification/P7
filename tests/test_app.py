import unittest
from unittest.mock import patch, MagicMock

from datetime import datetime

from app import (
    app,
    get_error_metrics,
    process_trajectories,
    run_algorithms,
    simplifiers,
    raw_routes,
)

from classes.route import Route
from classes.vessel_log import VesselLog

from tests.test_mock_vessel_logs import mock_vessel_logs


class AppTest(unittest.TestCase):
    """
    Tests for the algorithm processing logic in app.py.

    This class focuses on:
    - Testing individual helper functions (`get_error_metrics`, `process_trajectories`)
    - Testing the main orchestration function (`run_algorithms`)
    - Ensuring global state updates work as expected
    - Ensuring all tests run in isolation using mock database responses
    """

    @classmethod
    def setUp(self):
        """
        Runs before every test.
        Clears global state to ensure test isolation.
        """
        simplifiers.clear()
        raw_routes.clear()

    def test_get_error_metrics(self):
        """
        Ensures get_error_metrics(raw, simplified) always returns a list of:
            [ped_avg, ped_max, sed_avg, sed_max, comp_ratio]
        as floats.
        """
        # raw_routes format: {route_id: [VesselLog, ...]}
        raw = {1: mock_vessel_logs}

        # simplified uses the same logs for simplicity
        simplified = {1: mock_vessel_logs}

        metrics = get_error_metrics(raw, simplified)

        # Ensure five float values are returned
        self.assertEqual(len(metrics), 5)
        for value in metrics:
            self.assertIsInstance(value, float)
        # Since raw and simplified are identical, error metrics should be zero except comp_ratio
        self.assertEqual(metrics, [0.0, 0.0, 0.0, 0.0, 1.0])

    def test_process_trajectories(self):
        """
        Ensures process_trajectories:
        - Creates simplifiers for each algorithm
        - Appends points into each simplifier
        - Calls simplify() on each appended point
        - Updates raw_routes accordingly
        """
        routes = {1: mock_vessel_logs}
        algorithms = ["DR", "DP"]
        params = {"tolerance": 5, "epsilon": 5}

        # Patch simplify() to avoid modifying trajectories
        with patch(
            "algorithms.dead_reckoning.DeadReckoning.simplify"
        ) as dr_mock, patch("algorithms.dp.DouglasPeucker.simplify") as dp_mock:
            process_trajectories(routes, algorithms, params)

        # Check that simplifiers were created
        self.assertIn(1, simplifiers, "No entry created for route_id=1 in simplifiers")
        self.assertIn("DR", simplifiers[1], "Dead Reckoning simplifier missing")
        self.assertIn("DP", simplifiers[1], "Douglas–Peucker simplifier missing")

        # Check that simplify() was called once per appended point
        expected_calls = len(mock_vessel_logs)  # per algorithm
        self.assertEqual(
            dr_mock.call_count,
            expected_calls,
            "DR.simplify() call count mismatch, should correspond to number of appended points",
        )
        self.assertEqual(
            dp_mock.call_count,
            expected_calls,
            "DP.simplify() call count mismatch, should correspond to number of appended points",
        )

        # Ensure raw_routes was updated
        self.assertEqual(
            len(raw_routes[1]),
            len(mock_vessel_logs),
            "raw_routes not updated correctly",
        )

    @patch("app.get_all_vessels")
    @patch("app.get_vessel_logs")
    @patch("app.assign_routes")
    def test_run_algorithms(self, mock_assign, mock_get_logs, mock_get_all):
        """
        Ensures run_algorithms returns correct structure:

        {
            "DR": [...],
            "DP": [...],
            "raw": [...],
            "DR_error_metrics": [...],
            "DP_error_metrics": [...],
        }

        This test isolates DB calls and routing via patching.
        """
        # Mock vessel list
        mock_vessel = MagicMock()
        mock_vessel.imo = 1234567
        mock_get_all.return_value = {100: mock_vessel, 125: mock_vessel}

        # Mock returned logs from DB
        mock_get_logs.return_value = mock_vessel_logs

        # Mock assign_routes → single route
        mock_assign.return_value = {1: mock_vessel_logs}

        algorithms = ["DR", "DP"]
        params = {"tolerance": 5, "epsilon": 5}
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)

        result = run_algorithms(algorithms, start, end, params, [11111])

        # Core keys must exist
        self.assertIn("DR", result)
        self.assertIn("DP", result)
        self.assertIn("raw", result)
        self.assertIn("DR_error_metrics", result)
        self.assertIn("DP_error_metrics", result)

        # Validate structure of returned trajectories and metrics
        for key in ["DR", "DP", "raw"]:
            self.assertIsInstance(
                result[key],
                list,
                f"Result for {key} is not a list as expected",
            )
            for item in result[key]:
                self.assertIsInstance(
                    item,
                    list,
                    f"Item in result[{key}] is not a list as expected",
                )
                for log in item:
                    self.assertIsInstance(
                        log,
                        tuple,
                        f"Log in result[{key}] is not a tuple as expected",
                    )
                    self.assertEqual(
                        len(log),
                        3,
                        f"Log tuple in result[{key}] does not have 3 elements",
                    )
                    self.assertIsInstance(
                        log[0],
                        float,
                        f"Latitude in log tuple of result[{key}] is not a float",
                    )
                    self.assertIsInstance(
                        log[1],
                        float,
                        f"Longitude in log tuple of result[{key}] is not a float",
                    )
                    self.assertIsInstance(
                        log[2],
                        datetime,
                        f"Timestamp in log tuple of result[{key}] is not a datetime",
                    )
        for key in ["DR_error_metrics", "DP_error_metrics"]:
            self.assertIsInstance(
                result[key],
                list,
                f"Result for {key} is not a list as expected",
            )
            self.assertEqual(
                len(result[key]),
                5,
                f"Error metrics list for {key} does not have 5 elements",
            )
            for item in result[key]:
                self.assertIsInstance(
                    item,
                    float,
                    f"Item in result[{key}] is not a float as expected",
                )

        # Unrun algorithms should yield empty lists
        self.assertEqual(
            result["SQUISH"],
            [],
            "Expected empty trajectory list for unrun algorithm SQUISH",
        )

    @patch("app.get_all_vessels")
    @patch("app.get_vessel_logs")
    @patch("app.assign_routes")
    def test_algorithm_endpoint(self, mock_assign, mock_get_logs, mock_get_all):
        """
        Ensures /algorithm POST endpoint returns JSON containing expected keys.

        Uses Flask test_client to simulate HTTP request without running the server.
        """

        mock_vessel = MagicMock()
        mock_vessel.imo = 1234567
        mock_get_all.return_value = {100: mock_vessel, 125: mock_vessel}

        mock_get_logs.return_value = mock_vessel_logs
        mock_assign.return_value = {1: mock_vessel_logs}

        app.testing = True
        client = app.test_client()

        payload = {
            "params": {"tolerance": 10, "epsilon": 10},
            "start_date": "2024-01-01",
            "end_date": "2024-01-01 12:00:00",
            "algorithms": ["DR", "DP"],
        }

        response = client.post("/algorithm", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # Minimal sanity checks
        self.assertIn("DR", data)
        self.assertIn("DP", data)
        self.assertIn("raw", data)
        self.assertIn("DR_error_metrics", data)
        self.assertIn("DP_error_metrics", data)
        self.assertIsInstance(data["DR"], list)
        self.assertIsInstance(data["DP"], list)
        self.assertIsInstance(data["raw"], list)
        self.assertIsInstance(data["DR_error_metrics"], list)
        self.assertIsInstance(data["DP_error_metrics"], list)
        for item in data["DR"]:
            self.assertIsInstance(item, list)
            for log in item:
                self.assertIsInstance(log, list)
                self.assertEqual(len(log), 3)  # (lat, lon, ts)
                self.assertIsInstance(log[0], float)  # lat
                self.assertIsInstance(log[1], float)  # lon
                self.assertIsInstance(log[2], str)  # ts


if __name__ == "__main__":
    unittest.main()
