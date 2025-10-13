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

