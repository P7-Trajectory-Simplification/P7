import math
import unittest

import numpy as np
from pyproj import Geod

from algorithms.great_circle_math import magnitude, great_circle_distance, predict_sphere_movement, latlon_to_vector, point_to_great_circle, get_final_bearing
from tests.test_mock_vessel_logs import mock_vessel_logs
from geokernels.geodesics import geodesic_vincenty

class GreatCircleMathTest(unittest.TestCase):
    def setUp(self):
        self.lat1, self.lon1 = mock_vessel_logs[0].get_coords()
        self.lat2, self.lon2 = mock_vessel_logs[1].get_coords()
        self.lat3, self.lon3 = mock_vessel_logs[2].get_coords()
        self.vector = np.array(
            [
                np.cos(self.lat1) * np.cos(self.lon1),
                np.cos(self.lat1) * np.sin(self.lon1),
                np.sin(self.lat1),
            ]
        )





    def point_line_distance(self, point: tuple[float, float], segPoint1: tuple[float, float], segPoint2: tuple[float, float]) -> float:
        geod = Geod(ellps="WGS84")
        lat_p, lon_p = point
        lat1, lon1 = segPoint1
        lat2, lon2 = segPoint2
        # Forward azimuths and distance from start->end
        azi1, azi2, dist12 = geod.inv(lon1, lat1, lon2, lat2)

        # Project the point onto the line
        _, _, s13 = geod.inv(lon1, lat1, lon_p, lat_p)
        lonp_proj, latp_proj, _ = geod.fwd(lon1, lat1, azi1,
                                           s13 * np.cos(np.deg2rad(azi1 - geod.inv(lon1, lat1, lon_p, lat_p)[0])))

        # Compute cross-track distance (orthogonal)
        azi13, _, dist13 = geod.inv(lon1, lat1, lon_p, lat_p)
        xtd = np.arcsin(np.sin(dist13 / geod.a) * np.sin(np.deg2rad(azi13 - azi1))) * geod.a

        return abs(xtd)


    def test_magnitude(self):
        #Mag on latlon vector
        self.assertEqual(
            magnitude(self.vector),
            math.sqrt(self.vector[0] ** 2 + self.vector[1] ** 2 + self.vector[2] ** 2),
            "Magnitude function should fulfill the Pythagorean theorem on 3D vectors",
        )

        #Mag on known vector
        self.assertEqual(
            magnitude(np.array([2, 2, 2])),
            math.sqrt(2**2 + 2**2 + 2**2),
            "Magnitude function should fulfill the Pythagorean theorem on 3D vectors",
        )

    def test_latlon_to_vector(self):
        np.testing.assert_array_almost_equal(
            latlon_to_vector((self.lat1, self.lon1)),
            self.vector,
            decimal=6,
            err_msg="latlon_to_vector should convert latitude and longitude to 3D unit vector correctly",
        )

    def test_point_to_great_circle(self):
        distance_gc = point_to_great_circle((self.lat1, self.lon1), (self.lat2, self.lon2), (self.lat3, self.lon3))
        distance_compare = self.point_line_distance((self.lat3, self.lon3), (self.lat1, self.lon1), (self.lat2, self.lon2))
        self.assertAlmostEqual(
            distance_gc,
            distance_compare,
            delta=1,
            msg="point_to_great_circle should closely match geodesic cross-track distance results",
        )

    def test_great_circle_distance(self):
        #Compare to geodesic vincenty
        distance_gc = great_circle_distance((self.lat1, self.lon1), (self.lat2, self.lon2))
        distance_vincenty = np.float64(geodesic_vincenty((self.lat1, self.lon1), (self.lat2, self.lon2)))
        self.assertAlmostEqual(
            distance_gc,
            distance_vincenty,
            delta=1,
            msg="great_circle_distance should closely match geodesic_vincenty results",
        )

    def test_predict_sphere_movement(self):
        geod = Geod(ellps="WGS84")
        distance = 10000  # 10 km
        bearing = np.radians(90)  # east

        gc_lat_pred, gc_lon_pred = predict_sphere_movement((self.lat1, self.lon1), distance, bearing)
        ref_lat_pred, ref_lon_pred, _ = geod.fwd(self.lat1, self.lon1, bearing, distance, radians=True)

        ref_lat_pred = np.radians(ref_lat_pred)
        ref_lon_pred = np.radians(ref_lon_pred)

        self.assertLess(
            abs(gc_lat_pred - ref_lat_pred),
            np.float64(1),
            msg="predict_sphere_movement latitude should closely match Geod.fwd results",
        )
        self.assertLess(
            abs(gc_lon_pred - ref_lon_pred),
            np.float64(1),
            msg="predict_sphere_movement longitude should closely match Geod.fwd results",
        )

    def test_get_final_bearing(self):
        geod = Geod(ellps="WGS84")
        final_bearing_gc = get_final_bearing((self.lat1, self.lon1), (self.lat2, self.lon2))

        fwd_azimuth, back_azimuth, _ = geod.inv(self.lat1, self.lon1,
                                                self.lat2, self.lon2,
                                                radians=True)

        bearing_ref = np.radians(back_azimuth - 180) % (2 * np.pi)

        self.assertLess(
            abs(((final_bearing_gc - bearing_ref + np.pi) % (2 * np.pi)) - np.pi),
            np.float64(1),
            msg="get_final_bearing should closely match Geod.inv back azimuth results",
        )

if __name__ == '__main__':
    unittest.main()
