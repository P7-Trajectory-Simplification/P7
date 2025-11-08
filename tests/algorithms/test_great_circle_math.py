import unittest
import numpy as np
import math

from algorithms.great_circle_math import (
    magnitude,
    latlon_to_vector,
    great_circle_distance,
    predict_sphere_movement,
    point_to_great_circle,
    get_final_bearing, EARTH_RADIUS_METERS,
)

class GreatCircleMathUnitTest(unittest.TestCase):

    def setUp(self):
        self.e0 = (math.radians(0), math.radians(0)) # Equator, 0°E
        self.e45 = (math.radians(0), math.radians(45))  # Equator, 45°E
        self.e90 = (math.radians(0), math.radians(90)) # Equator, 90°E
        self.n0 = (math.radians(90), math.radians(0)) # North Pole

    def test_magnitude(self):
        v = np.array([3.0, 4.0, 0.0])
        self.assertEqual(magnitude(v), 5.0)
        self.assertAlmostEqual(magnitude(np.zeros(3)), 0.0)

    def test_latlon_to_vector_known_points(self):
        np.testing.assert_array_almost_equal(
            latlon_to_vector(self.e0), np.array([1.0, 0.0, 0.0]), decimal=6
        )

        np.testing.assert_array_almost_equal(
            latlon_to_vector(self.e90), np.array([0.0, 1.0, 0.0]), decimal=6
        )

        np.testing.assert_array_almost_equal(
            latlon_to_vector(self.n0), np.array([0.0, 0.0, 1.0]), decimal=6
        )

    def test_great_circle_distance_quarter_circumference(self):
        d = great_circle_distance(self.e0, self.e90)
        self.assertAlmostEqual(d, math.radians(90) * EARTH_RADIUS_METERS, delta=10)

    def test_predict_sphere_movement_equator(self):
        dist = math.pi * EARTH_RADIUS_METERS / 2
        bearing = math.radians(90)
        new_lat, new_lon = predict_sphere_movement(self.e0, dist, bearing)
        self.assertAlmostEqual(math.degrees(new_lat), 0, delta=0.1)
        self.assertAlmostEqual(math.degrees(new_lon), 90, delta=0.1)

    def test_point_to_great_circle_known_case(self):
        d = point_to_great_circle(self.e0, self.e90, self.e45)
        self.assertAlmostEqual(d, 0.0, delta=1e-6)

    def test_get_final_bearing_simple_case(self):
        self.assertAlmostEqual(
            math.degrees(get_final_bearing(self.n0, self.e90)) % 360,
            180,
            delta=1
        )

        self.assertAlmostEqual(
            math.degrees(get_final_bearing(self.e45, self.n0)) % 360,
            315,
            delta=1
        )

if __name__ == "__main__":
    unittest.main()
