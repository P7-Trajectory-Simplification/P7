import numpy as np
from geographiclib.geodesic import Geodesic

# we use a model of the Earth as defined by WGS84: Earth is an ellipsoid of rotation
# with a semi-major axis of 6378137.0 m and a semi-minor axis of approximately 6356752.314245 meters
geodesic = Geodesic.WGS84

# in a stroke of contrarian brilliance, geographicLib uses degrees instead of radians.
# We still assume the input will be given in radians, as that is what the other mathematical models expect.


# NOTE that we don't care about keyword arguments, but we still need to accept them for compatibility reasons, hence the **_
def geodesic_length(latlon_a, latlon_b, **_):
    latlons = np.rad2deg([*latlon_a, *latlon_b])
    return geodesic.Inverse(*latlons, outmask=geodesic.DISTANCE)['s12']


def geodesic_prediction(latlon, distance, bearing, **_):
    degree_arguments = np.rad2deg([*latlon, bearing])
    geodesic_dict = geodesic.Direct(*degree_arguments, distance)
    return np.deg2rad(geodesic_dict['lat2']), np.deg2rad(geodesic_dict['lon2'])


def geodesic_final_bearing(latlon_a, latlon_b):
    latlons = np.rad2deg([*latlon_a, *latlon_b])
    return np.deg2rad(geodesic.Inverse(*latlons, outmask=geodesic.AZIMUTH)['azi2'])


def point_to_geodesic(latlon_a, latlon_b, latlon_c, **_):
    # NOTE: This is the hard one. we can't rely on just geographicLib to solve this one,
    # so we use the algorithm from this paper:
    # https://www.researchgate.net/publication/321358300_Intersection_and_point-to-line_solutions_for_geodesics_on_the_ellipsoid
    pass


if __name__ == '__main__':
    # how far from university to Klarup
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
