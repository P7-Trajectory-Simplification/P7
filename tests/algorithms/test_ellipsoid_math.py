import unittest

import numpy as np

from algorithms.ellipsoid_math import geodesic_length, geodesic_prediction, geodesic_final_bearing, point_to_geodesic

class GreatCircleMathTest(unittest.TestCase):
    def setUp(self):
        print(
            geodesic_length(
                (np.deg2rad(57.011257), np.deg2rad(10.063530)),
                (np.deg2rad(57.012349), np.deg2rad(9.990929)),
            )
        )

        # from the university and 4500 meters East
        latitude, longitude = geodesic_prediction(
            (np.deg2rad(57.012313), np.deg2rad(9.991171)),
            4500,
            np.deg2rad(90),
        )
        print((np.rad2deg(latitude), np.rad2deg(longitude)))

        # the angle from AAU canteen to Cassiopeia (the building)
        bearing = geodesic_final_bearing(
            (np.deg2rad(57.015631), np.deg2rad(9.977710)),
            (np.deg2rad(57.012674), np.deg2rad(9.990636)),
        )
        print(np.rad2deg(bearing))

        # how far from university to the border (defined by a geodesic)
        print(
            point_to_geodesic(
                (np.radians(54.916584), np.radians(8.605293)),
                (np.radians(54.818675), np.radians(9.446560)),
                (np.radians(57.011476), np.radians(9.990813)),
            )
        )

if __name__ == '__main__':
    unittest.main()
