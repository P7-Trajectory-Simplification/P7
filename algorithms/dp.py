import rdp

def douglas_peucker(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    """
    Simplifies a given set of points using the Douglas-Peucker algorithm.

    Parameters:
    points (list of tuples): List of (x, y) coordinates representing the points.
    epsilon (float): The maximum distance threshold for simplification.

    Returns:
    list of tuples: Simplified list of points.
    """
    return rdp.rdp(points, epsilon=epsilon)