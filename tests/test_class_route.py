import unittest

from classes.route import Route
from tests.test_mock_vessel_logs import mock_vessel_logs

class RouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vessel_logs = mock_vessel_logs

    def test_routes(self):
        routeWithData = Route(trajectory=self.vessel_logs)

        # Check that the trajectory has been set correctly
        self.assertEqual(
            len(routeWithData.trajectory),
            len(self.vessel_logs)
        )

        # Check that to_list method returns correct data
        self.assertEqual(
            routeWithData.to_list()[0],
            (self.vessel_logs[0].lat, self.vessel_logs[0].lon, self.vessel_logs[0].ts)
        )

        self.assertEqual(
            routeWithData.to_list()[-1],
            (self.vessel_logs[-1].lat, self.vessel_logs[-1].lon, self.vessel_logs[-1].ts)
        )

        # Check the length of the list returned by to_list
        self.assertEqual(
            len(routeWithData.to_list()),
            len(self.vessel_logs)
        )

        emptyRoute = Route()
        self.assertEqual(len(emptyRoute.trajectory), 0)
        self.assertEqual(len(emptyRoute.to_list()), 0)


if __name__ == '__main__':
    unittest.main()
