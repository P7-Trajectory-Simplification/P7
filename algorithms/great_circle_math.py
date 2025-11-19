import numpy as np

# radius of the earth as defined by The International Union of Geodesy and Geophysics
EARTH_RADIUS_METERS = 6371e3

# NOTE: A great circle is a circular intersection of a sphere and a plane that passes through its center point.
# Any arc of a great circle is a geodesic of the sphere (A geodesic is, oversimplified, the shortest path between two points on a surface).
# Great circles, then, can be considered as spherical geometry's straight lines.
# Importantly, any two distinct points on a sphere that are not antipodal have a unique great circle that passes through both.

# NOTE: ALL FUNCTIONS THAT USE LATITUDE AND LONGITUDE EXPECT THEM TO BE EXPRESSED IN RADIANS!


def magnitude(vector: np.ndarray) -> float:
    '''Given a vector, return its magnitude.

    Parameters
    ----------
    vector : any numpy arraylike that supports dot and sqrt

    '''
    return np.sqrt(vector.dot(vector))


def latlon_to_vector(latlon: tuple[float, float]) -> np.ndarray:
    '''Given a latitude and longitude-pair, return a numpy array-representation of a 3D unit vector that corresponds to that latitude and longitude.
    Floating-point errors may occur, but from testing them seem very, very small.

    Parameters
    ----------
    latlon : _latitude and longitude-tuple_
        Latitude and longitude-pair
    '''
    latitude, longitude = latlon
    vector = np.array(
        [
            np.cos(latitude) * np.cos(longitude),
            np.cos(latitude) * np.sin(longitude),
            np.sin(latitude),
        ]
    )
    return np.divide(vector, magnitude(vector))


# used to be an implementation of https://web.archive.org/web/20171230114759/http://mathforum.org/library/drmath/view/51785.html
# old comments in case we need to restore this
# vector_n is normal to the plane of the great circle between A and B
# vector_n = np.cross(vector_a, vector_b) / magnitude(np.cross(vector_a, vector_b))

# N . C = cos(<NOC) with <NOC being the angle between N and C measured from the sphere's center
# angle_nc = np.arccos(vector_n.dot(vector_c))

# the difference between angle_nc and a right angle is the angular distance from C to the great circle between A and B
# distance = np.radians(90) - angle_nc

# we multiply by the radius and we're done


def point_to_great_circle(latlon_a: tuple[float, float], latlon_b: tuple[float, float], latlon_c: tuple[float, float], radius: float=EARTH_RADIUS_METERS, ignore_sign: bool=True):
    '''Given the latitude and longitudes of three points A, B, and C, where a great circle connects A and B,

    return the length of the geodesic from C to that great circle.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the great circle.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the great circle.
    latlon_c : _latitude and longitude-tuple_
        The latitude and longitude of the point whose distance to the great circle we want to know.
    radius   : _positive float or int_, optional
        The radius of the sphere where A and B are points. Defaults to 1.
    ignore_sign : _Boolean_, optional
        Depending on the order of a and b in input, the result may be positive or negative, but the absolute value will be the same.
        This argument forces the result to be nonnegative. Defaults to True.
    '''
    # Implementation of method explained in https://math.stackexchange.com/questions/337055/compute-minimum-distance-between-point-and-great-arc-on-sphere

    if equal_latlon(latlon_a, latlon_b):
        distance = great_circle_distance(latlon_a, latlon_b, radius=radius)
    else:
        # we transform the latlons into unit vectors coming from the center of the sphere
        vector_a = latlon_to_vector(latlon_a)
        vector_b = latlon_to_vector(latlon_b)
        vector_c = latlon_to_vector(latlon_c)

        distance = np.arcsin(
            (vector_c.dot(np.cross(vector_a, vector_b)))
            / magnitude(np.cross(vector_a, vector_b))
        )
    if ignore_sign:
        return np.abs(distance * radius)
    else:
        return distance * radius


def great_circle_distance(latlon_a: tuple[float, float], latlon_b: tuple[float, float], radius: float=EARTH_RADIUS_METERS) -> float:
    '''Given a pair of latitudes and longitudes describing points on a sphere A and B, computes the great circle-distance between those points
    i.e. the length of the geodesic connecting those points

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the great circle.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the great circle.
    radius   : _positive float or int_, optional
        The radius of the sphere where A and B are points. Defaults to 1.
    '''
    
    # implementation of method described in https://en.wikipedia.org/wiki/Great-circle_navigation
    latitude_a, longitude_a = latlon_a
    latitude_b, longitude_b = latlon_b
    longitude_delta = longitude_b - longitude_a
    y = np.sqrt(
        np.square(
            np.cos(latitude_a) * np.sin(latitude_b)
            - np.sin(latitude_a) * np.cos(latitude_b) * np.cos(longitude_delta)
        )
        + np.square(np.cos(latitude_b) * np.sin(longitude_delta))
    )
    x = np.sin(latitude_a) * np.sin(latitude_b) + np.cos(latitude_a) * np.cos(
        latitude_b
    ) * np.cos(longitude_delta)
    angular_difference = np.atan2(y, x)
    # multiply angular difference with radius to get the distance covered
    return angular_difference * radius


def predict_sphere_movement(latlon: tuple[float, float], distance: float, bearing: float, radius: float=EARTH_RADIUS_METERS) -> tuple[float, float]:
    '''Given a position on a sphere described by latitude and longitude, a distance value, and a bearing,
    return a tuple containing the latitude and longitude of the destination point.

    Parameters
    ----------
    latlon : _latitude and longitude-tuple_
        The latitude and longitude of the point where movement begins.
    distance : _type_
        The distance travelled during the movement.
    bearing : _type_
        The direction of the movement, measured in radians clockwise from the North Pole.
    radius   : _positive float or int_, optional
        The radius of the sphere used for calculations. Defaults to 1.
    '''  # TODO check if it's actually clockwise!
    latitude, longitude = latlon
    AB = distance / radius
    AN = np.radians(90) - latitude  # the colatitude of A
    angle_NAB = bearing  # np.radians(360) - bearing  # TODO explain what this angle is!
    BN = np.arccos(
        np.cos(AN) * np.cos(AB) + np.sin(AN) * np.sin(AB) * np.cos(angle_NAB)
    )  # the colatitude of B
    final_latitude = np.radians(90) - BN
    angle_BNA = np.arcsin((np.sin(angle_NAB) * np.sin(AB)) / np.sin(BN))
    final_longitude = angle_BNA + longitude
    return final_latitude, final_longitude


def get_final_bearing(latlon_a: tuple[float, float], latlon_b: tuple[float, float]) -> float:
    '''Given a pair of latitudes and longitudes describing points on a sphere A and B,
    computes the direction of the geodesic from A to B at point B i.e. the bearing of some hypothetical vehicle at point B.
    Note that bearing is measured clockwise from the north-direction, so 90 degrees corresponds to East and -90 degrees corresponds to West.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The starting point of our hypothetical vehicle's travel.
    latlon_b : _latitude and longitude-tuple_
        The endpoint of our hypothetical vehicle's travel. This function returns the vehicle's bearing at this point.
    '''
    # based on the method covered in https://geophydog.cool/post/geometry_on_a_sphere/#__2-the-azimuth-and-back-azimuth__
    # REVIEW maybe not the most prestigious source but their method *does* work.
    # NOTE the points have to be swapped in order to compute back-azimuth i.e. the bearing at the end of the path
    latitude_a, longitude_a = latlon_b
    latitude_b, longitude_b = latlon_a
    longitude_delta = longitude_b - longitude_a
    y = np.sin(longitude_delta) * np.cos(latitude_b)
    x = np.cos(latitude_a) * np.sin(latitude_b) - np.sin(latitude_a) * np.cos(
        latitude_b
    ) * np.cos(longitude_delta)
    back_azimuth = (
        np.arctan2(y, x) / (np.pi / np.radians(180)) + np.radians(360)
    ) % np.radians(360)
    # we reverse the back-azimuth to get the bearing
    return back_azimuth - np.radians(180)

def equal_latlon(a, b):
    """Safe equality check for tuple or numpy latlon pairs.
    Helper function for vectorized operations in error metrics."""
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.allclose(a, b)
    return a == b