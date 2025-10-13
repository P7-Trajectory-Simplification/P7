from datetime import datetime
from math import sqrt

def ped (point, start_seg, end_seg):
    """Point to segment Perpendicular Euclidean distance.

    Args:
        point (tuple): (x, y) coordinates of the point.
        start_seg (tuple): (x, y) coordinates of the start of the segment.
        end_seg (tuple): (x, y) coordinates of the end of the segment.

    Returns:
        float: The minimum Euclidean distance from the point to the segment.
    """
    x, y = point
    x1, y1 = start_seg
    x2, y2 = end_seg
    
    if (x1 == x2) and (y1 == y2):
        distance = sqrt((x - x1)**2 + (y - y1)**2)
        return distance
    
    # Projection factor t: how far along the segment the projection lies
    t = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / ((x2 - x1)**2 + (y2 - y1)**2)

    if t < 0:
        # Closest to the start of the segment
        distance = sqrt((x - x1)**2 + (y - y1)**2)
    elif t > 1:
        # Closest to the end of the segment
        distance = sqrt((x - x2)**2 + (y - y2)**2)
    else:
        # Calculate the projection of point onto the line defined by start_seg and end_seg
        distance = abs((y2-y1)*x - (x2-x1)*y + x2*y1 - y2*x1) / sqrt((y2-y1)**2 + (x2-x1)**2)

    return distance


def find_segment(point, trajectory):
    """Find the segment in the trajectory whose time interval is closest to the point's time."""
    point_time = point[2]
    min_time_diff = float('inf')
    closest_segment = None

    for i in range(len(trajectory) - 1):
        start = trajectory[i]
        end = trajectory[i + 1]
        # Find time difference between point_time and the segment's interval
        if start[2] <= point_time <= end[2]:
            return (start, end)
        """else:
            # If outside, compute how far the point_time is from the nearest endpoint
            time_diff = min(abs((point_time - start[2]).total_seconds()),
                            abs((point_time - end[2]).total_seconds()))
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_segment = (start, end)

    return closest_segment"""
    print("Point time is outside the segment time interval.")
    return None
        
def ped_results(trajectory1, trajectory2):
    """Calculate the average Point to segment Euclidean distance between two trajectories and the maximum Point to segment Euclidean distance between two trajectories.

    Args:
        trajectory1 (list): List of (x, y, timestamp) tuples for the first trajectory.
        trajectory2 (list): List of (x, y, timestamp) tuples for the second trajectory.

    Returns:
        float: The average PED between the two trajectories.
    """
    max_distance = 0
    total_distance = 0
    count = 0

    for point in trajectory1:
        segment = find_segment(point, trajectory2)
        if segment is not None:
            start_seg, end_seg = segment
            distance = ped((point[0], point[1]), (start_seg[0], start_seg[1]), (end_seg[0], end_seg[1]))
            total_distance += distance
            count += 1
        if distance > max_distance:
                max_distance = distance

    if count == 0:
        return float('inf')  # No valid segments found

    avg_distance = total_distance / count
    return avg_distance, max_distance
