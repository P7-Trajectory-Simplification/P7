
from classes.route import Route
from classes.vessel_log import VesselLog


def uniform_sampling(points: list[VesselLog], sampling_rate: float) -> list[VesselLog]:
    '''
    Simplifies a given set of points using uniform sampling.

    Parameters
    ---------
    points (list of VesselLog): List of VesselLog objects representing the points.
    sampling_rate (float): The sampling_rate (e.g., every nth point).

    Returns
    ---------
    list of VesselLog: Simplified list of points.
    '''
    if sampling_rate <= 0:
        raise ValueError("Frequency must be a positive number.")

    sampled_points = []
    for i in range(0, len(points), int(sampling_rate)):
        sampled_points.append(points[i])

    # Ensure the last point is included
    if points[-1] not in sampled_points:
        sampled_points.append(points[-1])

    return sampled_points

def run_uniform_sampling(route: Route, params: dict) -> Route:
    simplified_trajectory = uniform_sampling(route.trajectory, params["sampling_rate"])
    return Route(simplified_trajectory)