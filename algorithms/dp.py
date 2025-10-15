from algorithms.great_circle_math import point_to_great_circle, EARTH_RADIUS_METERS
from vessel_log import VesselLog
import numpy as np


def douglas_peucker(points: list[VesselLog], epsilon: float) -> list[VesselLog]:
    '''
    Simplifies a given set of points using the Douglas-Peucker algorithm.

    Parameters:
    points (list of tuples): List of (lat, lon) coordinates representing the points.
    epsilon (float): The maximum distance threshold for simplification.

    Returns:
    list of tuples: Simplified list of points.
    '''
    dmax = 0
    index = 0
    end = len(points) - 1
    for i in range(1, end):
        # Calculate the perpendicular distance from point to line segment
        d = np.abs(point_to_great_circle(points[0].get_coords(), points[end].get_coords(), points[i].get_coords()))
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        rec_results1 = douglas_peucker(points[:index + 1], epsilon)
        rec_results2 = douglas_peucker(points[index:], epsilon)

        return rec_results1[:-1] + rec_results2
    return [points[0], points[end]]


