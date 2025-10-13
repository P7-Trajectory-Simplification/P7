import numpy as np

# radius of the earth as defined by The International Union of Geodesy and Geophysics
EARTH_RADIUS_METERS = 6371e3

# NOTE: A great circle is a circular intersection of a sphere and a plane that passes through its center point.
# Any arc of a great circle is a geodesic of the sphere (A geodesic is, oversimplified, the shortest path between two points on a surface).
# Great circles, then, can be considered as spherical geometry's straight lines.
# Importantly, any two distinct points on a sphere that are not antipodal have a unique great circle that passes through both.

# NOTE: ALL FUNCTIONS THAT USE LATITUDE AND LONGITUDE EXPECT THEM TO BE EXPRESSED IN RADIANS!


def magnitude(vector):
    """Given a vector, return its magnitude.

    Parameters
    ----------
    vector : any numpy arraylike that supports dot and sqrt

    """
    return np.sqrt(vector.dot(vector))


def latlon_to_vector(latlon):
    """Given a latitude and longitude-pair, return a numpy array-representation of a 3D unit vector that corresponds to that latitude and longitude.
    Floating-point errors may occur, but from testing them seem very very small.

    Parameters
    ----------
    latlon : _latitude and longitude-tuple_
        Latitude and longitude-pair
    """
    latitude, longitude = latlon
    vector = np.array(
        [
            np.cos(latitude) * np.cos(longitude),
            np.cos(latitude) * np.sin(longitude),
            np.sin(latitude),
        ]
    )
    return np.divide(vector, magnitude(vector))


def point_to_great_circle(latlon_a, latlon_b, latlon_c, radius=1):
    """Given the latitude and longitudes of three points A, B, and C, where a great circle connects A and B,
    return the length of the geodesic from C to that great circle.
    Implementation of method explained in https://web.archive.org/web/20171230114759/http://mathforum.org/library/drmath/view/51785.html

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
    """
    # we transform the latlons into unit vectors coming from the center of the sphere
    vector_a = latlon_to_vector(latlon_a)
    vector_b = latlon_to_vector(latlon_b)
    vector_c = latlon_to_vector(latlon_c)

    # vector_n is normal to the plane of the great circle between A and B
    vector_n = np.cross(vector_a, vector_b) / magnitude(np.cross(vector_a, vector_b))

    # N . C = cos(<NOC) with <NOC being the angle between N and C measured from the sphere's center
    angle_nc = np.arccos(vector_n.dot(vector_c))

    # the difference between angle_nc and a right angle is the angular distance from C to the great circle between A and B
    distance = np.radians(90) - angle_nc

    # we multiply by the radius and we're done
    return distance * radius


def great_circle_distance(latlon_a, latlon_b, radius=1):
    """Given a pair of latitudes and longitudes describing points on a sphere A and B, computes the great circle-distance between those points
    i.e. the length of the geodesic connecting those points

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the great circle.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the great circle.
    radius   : _positive float or int_, optional
        The radius of the sphere where A and B are points. Defaults to 1.
    """
    # implementation of method as described in https://en.wikipedia.org/wiki/N-vector#Example_1:_Great_circle_distance
    vector_a = latlon_to_vector(latlon_a)
    vector_b = latlon_to_vector(latlon_b)
    angular_difference = np.arctan(
        magnitude(np.cross(vector_a, vector_b)) / vector_a.dot(vector_b)
    )
    return angular_difference * radius


def predict_sphere_movement(latlon, distance, bearing, radius=1):
    """Given a position on a sphere described by latitude and longitude, a distance value, and a bearing,
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
    """  # TODO check if it's actually clockwise!
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
    return (final_latitude, final_longitude)


def get_final_bearing(latlon_a, latlon_b):
    """Given a pair of latitudes and longitudes describing points on a sphere A and B,
    computes the direction of the geodesic from A to B at point B i.e. the bearing of some hypothetical vehicle at point B.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The starting point of our hypothetical vehicle's travel.
    latlon_b : _latitude and longitude-tuple_
        The endpoint of our hypothetical vehicle's travel. This function returns the vehicle's bearing at this point.
    """
    latitude_a, longitude_a = latlon_a
    _, longitude_b = latlon_b
    angle_ANB = longitude_b - longitude_a
    AN = np.radians(90) - latitude_a
    # we're just interested in angles right now, so we use greatCircleDistance's default radius of 1 to make things easier
    AB = great_circle_distance(latlon_a, latlon_b)
    # using the sine rule we can find the angle ABN
    angle_ABN = np.arcsin((np.sin(angle_ANB) * np.sin(AN)) / np.sin(AB))
    # the new bearing is exactly ABN
    return angle_ABN


if __name__ == "__main__":
    # how far from university to the border (defined by a geodesic)
    print(
        point_to_great_circle(
            (np.radians(54.916584), np.radians(8.605293)),
            (np.radians(54.818675), np.radians(9.446560)),
            (np.radians(57.011476), np.radians(9.990813)),
            radius=EARTH_RADIUS_METERS,
        )
    )

    # how far from university to Klarup
    print(
        point_to_great_circle(
            (np.radians(57.011257), np.radians(10.063530)),
            (np.radians(57.012349), np.radians(9.990929)),
            radius=EARTH_RADIUS_METERS,
        )
    )

    # from the university and 4500 meters East
    latitude, longitude = predict_sphere_movement(
        (np.radians(57.012313), np.radians(9.991171)),
        4500,
        np.radians(90),
        radius=EARTH_RADIUS_METERS,
    )
    print((np.rad2deg(latitude), np.rad2deg(longitude)))

    bearing = get_final_bearing(
        (np.radians(57.012313), np.radians(9.991171)),
        (np.radians(57.011549), np.radians(10.057820)),
    )
    print(np.rad2deg(bearing))
