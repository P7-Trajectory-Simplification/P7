
from math import sqrt
import math

from algorithms.great_circle_math import great_circle_distance
from classes.route import Route

'''
def sed(point, simplified_point):
    Synchronized Euclidean distance.

    Parameters:
        point (tuple): (x, y, t) coordinates of the original point.
        simplified_point (tuple): (x, y, t) coordinates of the corresponding simplified point.

    Returns:
        float: The Euclidean distance between the original point and the simplified point.
    
    x, y, _ = point
    x_s, y_s, _ = simplified_point
    
    # Calculates the Euclidean distance between the two points
    distance = sqrt((x - x_s)**2 + (y - y_s)**2)
    return distance
'''

def find_simplified_point(point, trajectory):
    '''Find the point in the simplified trajectory whose time is closest to the point's time.'''
    point_time = point.ts
    min_time_diff = None
    closest_point = None

    for i in range(len(trajectory) - 1):
        simplified_point = trajectory[i]
        # Find time difference between point_time and the simplified point's time
        if simplified_point.ts == point_time:
            return (simplified_point)
        else:
            # If outside, compute how far the point_time is from the simplified point's time
            time_diff = abs((point_time - simplified_point.ts).total_seconds())
            if min_time_diff is None:
                min_time_diff = time_diff
                closest_point = simplified_point
            elif time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_point = simplified_point

    return closest_point

def sed_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    '''Calculate the average Point to simplified point Euclidean distance between two trajectories
    and the maximum Point to simplified point Euclidean distance between two trajectories.

    Parameters:
        trajectory1 (list): List of (x, y, timestamp) tuples for the raw data trajectory.
        trajectory2 (list): List of (x, y, timestamp) tuples for the simplified trajectory.

    Returns:
        float: The average SED between the two trajectories and the max distance.
    '''
    max_distance = 0
    total_distance = 0
    count = 0

    for i, raw_route in enumerate(raw_data_routes):
        simplified_route = simplified_routes[i]
        for point in raw_route.trajectory:
            simplified_point = find_simplified_point(point, simplified_route.trajectory)
            distance = great_circle_distance(point.get_coords(), simplified_point.get_coords())
            total_distance += distance
            count += 1
            if distance > max_distance:
                    max_distance = distance
    if count == 0:
        return 0, 0  # both average and max are zero 
    avg_distance = total_distance / count
    return round(avg_distance, 2), round(max_distance, 2)