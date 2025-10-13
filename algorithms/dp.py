from algorithms.great_circle_math import point_to_great_circle
from vessel_log import VesselLog


def douglas_peucker(points: list[VesselLog], epsilon: float) -> list[VesselLog]:
    """
    Simplifies a given set of points using the Douglas-Peucker algorithm.

    Parameters:
    points (list of tuples): List of (lat, lon) coordinates representing the points.
    epsilon (float): The maximum distance threshold for simplification.

    Returns:
    list of tuples: Simplified list of points.
    """
    dmax = 0
    index = 0
    end = len(points) - 1
    for i in range(1, end):
        # Calculate the perpendicular distance from point to line segment
        d = point_to_great_circle(points[0].get_coords(), points[end].get_coords(), points[i].get_coords())
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        rec_results1 = douglas_peucker(points[:index + 1], epsilon)
        rec_results2 = douglas_peucker(points[index:], epsilon)

        return rec_results1[:-1] + rec_results2
    return [points[0], points[end]]


def haversine_distance(first: VesselLog, second: VesselLog):
    """
    Calculates the Haversine distance between two points on the Earth.

    Parameters:
    points (tuple): The (lat, lon) coordinates of the first point.
    start (tuple): The (lat, lon) coordinates of the second point.

    Returns:
    float: The Haversine distance in meters.
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # Radius of the Earth in meters

    dlat = radians(second.lat - first.lat)
    dlon = radians(second.lon - first.lon)

    a = sin(dlat / 2) ** 2 + cos(radians(first.lat)) * cos(radians(second.lat)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def perpendicular_distance(points: VesselLog, start: VesselLog, end: VesselLog) -> float:
    """
    Calculates the perpendicular distance from a point to a line segment.

    Parameters:
    point (tuple): The (lat, lon) coordinates of the point.
    start (tuple): The (lat, lon) coordinates of the start of the line segment.
    end (tuple): The (lat, lon) coordinates of the end of the line segment.

    Returns:
    float: The perpendicular distance from the point to the line segment.
    """
    if start == end:
        return haversine_distance(points, start)

    num = abs((end.lon - start.lon) * points.lat - (end.lat - start.lat) * points.lon + end.lat * start.lon - end.lon * start.lat)
    den = ((end.lon - start.lon) ** 2 + (end.lat - start.lat) ** 2) ** 0.5
    return num / den
