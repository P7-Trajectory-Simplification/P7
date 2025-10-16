
from math import sqrt


def sed(point, simplified_point):
    """Synchronized Euclidean distance.

    Args:
        point (tuple): (x, y, t) coordinates of the original point.
        simplified_point (tuple): (x, y, t) coordinates of the corresponding simplified point.

    Returns:
        float: The Euclidean distance between the original point and the simplified point.
    """
    x, y, _ = point
    x_s, y_s, _ = simplified_point
    
    # Calculates the Euclidean distance between the two points
    distance = sqrt((x - x_s)**2 + (y - y_s)**2)
    return distance


def find_simplified_point(point, trajectory):
    """Find the point in the simplified trajectory whose time is closest to the point's time."""
    point_time = point[2]
    min_time_diff = float('inf')
    closest_point = None

    for i in range(len(trajectory) - 1):
        simplified_point = trajectory[i]
        # Find time difference between point_time and the simplified point's time
        if simplified_point[2] == point_time:
            return (simplified_point)
        else:
            # If outside, compute how far the point_time is from the simplified point's time
            time_diff = abs((point_time - simplified_point[2]).total_seconds())
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_point = simplified_point

    return closest_point

def sed_results(raw_data_trajectory, simplified_trajectory):
    """Calculate the average Point to simplified point Euclidean distance between two trajectories
    and the maximum Point to simplified point Euclidean distance between two trajectories.

    Args:
        trajectory1 (list): List of (x, y, timestamp) tuples for the raw data trajectory.
        trajectory2 (list): List of (x, y, timestamp) tuples for the simplified trajectory.

    Returns:
        float: The average SED between the two trajectories and the max distance.
    """
    max_distance = 0
    total_distance = 0
    count = 0

    for point in raw_data_trajectory:
        simplified_point = find_simplified_point(point, simplified_trajectory)
        distance = sed(point, simplified_point)
        total_distance += distance
        count += 1
        if distance > max_distance:
                max_distance = distance

    avg_distance = total_distance / count
    return avg_distance, max_distance