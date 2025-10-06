from algorithms.Point import Point
from algorithms.euclidean_distance import update_sed


def squish(points: list[Point], buffer_size: int):
    """
    :param points: iterable of Point(x, y, t)
    :param buffer_size: integer, maximum buffer size
    :return: simplified trajectory (list of Point)
    """
    B = []

    for p in points:
        B.append(p)

        if len(B) >= 2:
            update_sed(B, len(B) - 2)

        if len(B) > buffer_size:
            # Find point with the smallest SED (except first and last)
            min_index = min(range(1, len(B) - 1), key=lambda i: B[i].sed)
            B.pop(min_index)
            # Update SED of neighbors
            if min_index - 1 > 0:
                update_sed(B, min_index - 1)
            if min_index < len(B) - 1:
                update_sed(B, min_index)

    return B