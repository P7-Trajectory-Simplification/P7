def douglas_peucker(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
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
        d = perpendicular_distance(points[i], points[0], points[end])
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        rec_results1 = douglas_peucker(points[:index + 1], epsilon)
        rec_results2 = douglas_peucker(points[index:], epsilon)

        return rec_results1[:-1] + rec_results2
    return [points[0], points[end]]


def haversine_distance(points, start):
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
    lat1, lon1 = points
    lat2, lon2 = start

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def perpendicular_distance(points: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
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

    num = abs((end[1] - start[1]) * points[0] - (end[0] - start[0]) * points[1] + end[0] * start[1] - end[1] * start[0])
    den = ((end[1] - start[1]) ** 2 + (end[0] - start[0]) ** 2) ** 0.5
    return num / den
