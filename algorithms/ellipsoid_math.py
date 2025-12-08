import numpy as np
from geographiclib.geodesic import Geodesic

# we use a model of the Earth as defined by WGS84: Earth is an ellipsoid of rotation
# with a semi-major axis of 6378137.0 m and a semi-minor axis of approximately 6356752.314245 meters
geodesic = Geodesic.WGS84

# in a stroke of contrarian brilliance, geographicLib uses degrees instead of radians.
# We still assume the input will be given in radians, as that is what the other mathematical models expect.


# NOTE that we don't care about keyword arguments, but we still need to accept them for compatibility reasons, hence the **_
def geodesic_length(latlon_a, latlon_b, **_):
    """Given the latitudes and longitudes of two points A and B on the WGS84-ellipsoid, return the minimum distance between them
    i.e. the length of the geodesic AB. This is a partial solution to the inverse geodesic problem.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the geodesic AB.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the geodesic AB.
    """
    latlons = np.rad2deg([*latlon_a, *latlon_b])
    return geodesic.Inverse(*latlons, outmask=geodesic.DISTANCE)["s12"]


def geodesic_prediction(latlon, distance, bearing, **_):
    """Given the latitude and longitude of a point on the WGS84-ellipsoid, a distance value, and a bearing,
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
    """
    degree_arguments = np.rad2deg([*latlon, bearing])
    geodesic_dict = geodesic.Direct(*degree_arguments, distance)
    return np.deg2rad(geodesic_dict["lat2"]), np.deg2rad(geodesic_dict["lon2"])


def geodesic_final_bearing(latlon_a, latlon_b):
    """Given the latitudes and longitudes of two points A and B on the WGS84-ellipsoid,
    return the second azimuth of the geodesic AB i.e. the bearing from B to A.
    This is a partial solution to the inverse geodesic problem.

    Parameters
    ----------
    latlon_a : _latitude and longitude-tuple_
        The latitude and longitude of the first point on the geodesic AB.
    latlon_b : _latitude and longitude-tuple_
        The latitude and longitude of the second point on the geodesic AB.
    """
    latlons = np.rad2deg([*latlon_a, *latlon_b])
    return np.deg2rad(geodesic.Inverse(*latlons, outmask=geodesic.AZIMUTH)["azi2"])


def point_to_geodesic(
    latlon_a: tuple[float, float],
    latlon_b: tuple[float, float],
    latlon_p: tuple[float, float],
    tol=1e-6,
):
    """
    Robust ellipsoidal point-to-segment distance.
    Inputs: (lat, lon) in radians.
    Output: distance in meters.
    """
    # Convert radians → degrees for GeographicLib
    lat_a, lon_a = np.degrees(latlon_a)
    lat_b, lon_b = np.degrees(latlon_b)
    lat_p, lon_p = np.degrees(latlon_p)

    # Degenerate case: A == B
    if lat_a == lat_b and lon_a == lon_b:
        return geodesic.Inverse(lat_a, lon_a, lat_p, lon_p)["s12"]

    # Geodesic AB info
    inv_ab = geodesic.Inverse(lat_a, lon_a, lat_b, lon_b)
    s_ab = inv_ab["s12"]  # total length of AB (meters)
    azi_ab = inv_ab["azi1"]  # azimuth A→B (degrees)

    # Parameterize AB as s ∈ [0, s_ab]
    line_ab = geodesic.Line(lat_a, lon_a, azi_ab)

    # The function to minimize: squared ellipsoidal distance
    def dist2(s):
        pt = line_ab.Position(s, outmask=Geodesic.LATITUDE | Geodesic.LONGITUDE)
        d = geodesic.Inverse(pt["lat2"], pt["lon2"], lat_p, lon_p)["s12"]
        return d * d

    # Golden-section search on [0, s_ab]
    phi = (1 + 5**0.5) / 2
    invphi = 1 / phi

    a, b = 0.0, s_ab
    c = b - invphi * (b - a)
    d = a + invphi * (b - a)
    fc = dist2(c)
    fd = dist2(d)

    # Iterate in s until interval length < tol
    # tol is in *meters of arc length*, so extremely tight
    while abs(b - a) > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - invphi * (b - a)
            fc = dist2(c)
        else:
            a, c, fc = c, d, fd
            d = a + invphi * (b - a)
            fd = dist2(d)

    # Best arc length
    s_star = 0.5 * (a + b)

    # Compute final perpendicular distance
    pt = line_ab.Position(s_star, outmask=Geodesic.LATITUDE | Geodesic.LONGITUDE)
    return geodesic.Inverse(pt["lat2"], pt["lon2"], lat_p, lon_p)["s12"]
