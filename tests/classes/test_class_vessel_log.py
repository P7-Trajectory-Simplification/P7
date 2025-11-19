import unittest

from tests.test_mock_vessel_logs import mock_vessel_logs

class VesselLogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vessel_logs = mock_vessel_logs

    def test_vessel_logs(self):
        for log in self.vessel_logs:
            self.assertIsInstance(log.lat, float)
            self.assertIsInstance(log.lon, float)
            self.assertIsNotNone(log.ts)

            coords = log.get_coords()
            self.assertIsInstance(coords, tuple)
            self.assertEqual(len(coords), 2)
            self.assertIsInstance(coords[0], float)
            self.assertIsInstance(coords[1], float)


if __name__ == '__main__':
    unittest.main()
