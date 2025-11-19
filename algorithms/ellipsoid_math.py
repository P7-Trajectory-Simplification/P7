import numpy as np
from geographiclib.geodesic import Geodesic
# we use a model of the Earth as defined by WGS84: Earth is an ellipsoid of rotation
# with a semi-major axis of 6378137.0 m and a semi-minor axis of approximately 6356752.314245 meters
geodesic = Geodesic.WGS84

# in a stroke of contrarian brilliance, geographicLib uses degrees instead of radians.
# We still assume the input will be given in radians, as that is what the other mathematical models expect.


# NOTE that we don't care about keyword arguments, but we still need to accept them for compatibility reasons, hence the **_
def geodesic_length(latlon_a, latlon_b, **_):
    '''Given the latitudes and longitudes of two points A and B on the WGS84-ellipsoid, return the minimum distance between them
    i.e. the length of the geodesic AB. This is a partial solution to the inverse geodesic problem.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the geodesic AB.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the geodesic AB.
    '''
    latlons = np.rad2deg([*latlon_a, *latlon_b])
    return geodesic.Inverse(*latlons, outmask=geodesic.DISTANCE)['s12']


def geodesic_prediction(latlon, distance, bearing, **_):
    '''Given the latitude and longitude of a point on the WGS84-ellipsoid, a distance value, and a bearing,
    return a tuple containing the latitude and longitude of the destination point.
    This is a partial solution to the direct geodesic problem.

    Parameters
    ----------
    latlon : _latitude and longitude-tuple_
        The latitude and longitude of the point where movement begins.
    distance : _type_
        The distance travelled during the movement, measured in meters.
    bearing : _type_
        The direction of the movement, measured in radians clockwise from the North Pole.
    '''
    degree_arguments = np.rad2deg([*latlon, bearing])
    geodesic_dict = geodesic.Direct(*degree_arguments, distance)
    return np.deg2rad(geodesic_dict['lat2']), np.deg2rad(geodesic_dict['lon2'])


def geodesic_final_bearing(latlon_a, latlon_b):
    '''Given the latitudes and longitudes of two points A and B on the WGS84-ellipsoid,
    return the second azimuth of the geodesic AB i.e. the bearing from B to A.
    This is a partial solution to the inverse geodesic problem.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the geodesic AB.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the geodesic AB.
    '''
    latlons = np.rad2deg([*latlon_a, *latlon_b])
    return np.deg2rad(geodesic.Inverse(*latlons, outmask=geodesic.AZIMUTH)['azi2'])


def point_to_geodesic(latlon_a, latlon_b, latlon_p, approximation_error=1e-5, **_):
    '''Given the latitudes and longitudes of three points A, B, and P on the WGS84-ellipsoid,
    return the length of the geodesic PX such that X is on the geodesic AB and forms a right angle between A and P.
    In other words: The minimum distance from P to AB across the surface of the ellipsoid.
    Note that the value returned by this function is an approximation, but still very precise,
    computed by pushing A towards X until they are sufficiently close, then finding the distance from A to P.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the geodesic AB.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the geodesic AB.
    latlon_p : _latitude and longitude-tuple_
        The latitude and longitude of the point whose minimum surface distance to AB we want to know.
    approximation_error : _float_
        The function iterates until the difference between A and X is less than this value.
        Lower values mean more iterations but also a more accurate result. Default is 1e-5.
    '''
    # NOTE: This is the hard one. we can't rely on just geographicLib to solve this one,
    # so we use the algorithm from this paper:
    # https://www.researchgate.net/publication/321358300_Intersection_and_point-to-line_solutions_for_geodesics_on_the_ellipsoid

    # we use the semimajor axis of the WGS84-ellipsoid as an approximation for the radius of a sphere later
    R = geodesic.a
    # we load our longitudes as degrees this time, to be compatible with geographicLib
    latitude_a, longitude_a = np.degrees(latlon_a)
    latitude_b, longitude_b = np.degrees(latlon_b)
    latitude_p, longitude_p = np.degrees(latlon_p)

    s_AX = np.inf
    while np.abs(s_AX) > approximation_error:
        # we start our iteration by finding some angles and distances we need later
        AP_inverse = geodesic.Inverse(latitude_a, longitude_a, latitude_p, longitude_p)
        s_AP = AP_inverse['s12']
        azimuth_AP = AP_inverse['azi1']
        AB_inverse = geodesic.Inverse(latitude_a, longitude_a, latitude_b, longitude_b)
        azimuth_AB = AB_inverse['azi1']
        angle_A = np.radians(azimuth_AP - azimuth_AB)
        # we've got the essentials now, so let's find an approximation for the distance from point P to the closest point X on geodesic AB
        s_PX = R * np.arcsin(np.sin(s_AP / R) * np.sin(angle_A))
        # with s_PX, we can approximate the distance from A to X
        y = np.sin(((np.pi / 2) + angle_A) / 2) * np.tan((s_AP - s_PX) / (2 * R))
        x = np.sin(((np.pi / 2) - angle_A) / 2)
        s_AX = 2 * R * np.arctan(y / x)
        # now we replace our point A with a new point on geodesic AB that is a distance of s_AX away from A.
        # We're essentially moving A towards point X while staying on the geodesic
        AX_direct = geodesic.Direct(latitude_a, longitude_a, azimuth_AB, s_AX)
        latitude_a = AX_direct['lat2']
        longitude_a = AX_direct['lon2']

    # once we have moved A close enough to X, we can return the distance from A to P as the minimum distance from P to geodesic AB
    return geodesic.Inverse(
        latitude_a, longitude_a, latitude_p, longitude_p, outmask=geodesic.DISTANCE
    )['s12']
