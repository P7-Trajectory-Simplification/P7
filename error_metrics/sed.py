from concurrent.futures import ProcessPoolExecutor
import numpy as np
from algorithms.great_circle_math import (
    get_final_bearing,
    great_circle_distance,
    predict_sphere_movement,
)
from classes.route import Route
from classes.vessel_log import VesselLog


def slerp(A: tuple[float, float], B: tuple[float, float], alpha: float, math: dict):
    '''Linearly interpolate between two latitudes and longitudes on a sphere.

    Parameters
    ----------
    A :  _latitude and longitude-tuple_
        The point to interpolate from.
    B :  _latitude and longitude-tuple_
        The point to interpolate to.
    alpha : float in range [0,1]
        How far to interpolate: 0.0 returns A, and 1.0 returns B, 0.5 returns the point exactly between A and B.

    Returns
    -------
    _latitude and longitude-tuple_
        The interpolated point.
    '''
    # find out how far from A we should end up
    distance = alpha * great_circle_distance(A, B)
    # find the direction from A to B
    bearing = get_final_bearing(B, A) + np.radians(180)
    # find the point at the given distance from A in the direction of B
    return predict_sphere_movement(A, distance, bearing)


def interpolate_simplified_points_vectorized(raw_times, simp_times, simp_latlon, math):
    '''For each raw timestamp, return the spherical interpolated point
    on the simplified trajectory at that timestamp.
    '''

    # Find segment index k such that simp_times[k] <= raw < simp_times[k+1]
    idx = np.searchsorted(simp_times, raw_times, side="right") - 1

    # Clamp indices to valid range
    idx = np.clip(idx, 0, len(simp_times) - 2)

    t0 = simp_times[idx]
    t1 = simp_times[idx + 1]

    # Compute the time diffrence between segment endpoints
    dt = t1 - t0

    # Boolean mask for zero dt (duplicate timestamps in simplified trajectory)
    zero_dt = dt == 0

    # Creating alpha array with same shape as dt, initialized to zeros
    alpha = np.zeros_like(dt, dtype=float)

    # Compute alpha only where dt != 0
    valid = ~zero_dt
    alpha[valid] = (raw_times[valid] - t0[valid]) / dt[valid]

    # Clip to [0,1]
    alpha = np.clip(alpha, 0.0, 1.0)

    # Allocate result
    result = np.zeros((len(raw_times), 2))

    # Interpolate each point with SLERP
    for i in range(len(raw_times)):
        p0 = simp_latlon[idx[i]]
        p1 = simp_latlon[idx[i] + 1]
        result[i] = slerp(p0, p1, alpha[i], math)

    return result


def sed_single_route_vectorized(
    raw_route: list[VesselLog], simplified_route: list[VesselLog], math: dict
) -> tuple[float, float, int]:
    '''Compute SED for a single route (vectorized).
    Using vectorized simplified point lookup and great-circle distance computation.
    Returns average distance, max distance, and count of points.'''

    # Return average distance, max distance, count as 0, if either route is empty.
    if len(raw_route) == 0 or len(simplified_route) == 0:
        return 0.0, 0.0, 0

    # Convert to numpy arrays for vectorized operations
    raw_latlon = np.array([p.get_coords() for p in raw_route])
    simplified_latlon = np.array([p.get_coords() for p in simplified_route])
    raw_times = np.array([p.ts.timestamp() for p in raw_route])
    simplified_times = np.array([p.ts.timestamp() for p in simplified_route])

    # Gets an array of simplified point indices for each raw point
    interp_points = interpolate_simplified_points_vectorized(
        raw_times, simplified_times, simplified_latlon, math
    )

    # Compute distances using great_circle_distance
    distances = np.array(
        [
            math["point_to_point_distance"](interp_points[i], raw_latlon[i])
            for i in range(len(raw_latlon))
        ]
    )

    return np.mean(distances), np.max(distances), len(distances)


def sed_results(
    raw_data_routes: dict[int, list[VesselLog]],
    simplified_routes: dict[int, list[VesselLog]],
    math: dict
) -> tuple[float, float]:
    '''Calculate the average Point to simplified point Euclidean distance between two trajectories
    and the maximum Point to simplified point Euclidean distance between two trajectories.

    Returns:
        tuple with floats: The average SED between the two trajectories and the max distance.
    '''
    results = [
        sed_single_route_vectorized(raw_data_routes[k], simplified_routes[k], math)
        for k in raw_data_routes
    ]
    # If no results were computed, return zeros, happens if no matching routes or all empty
    if not results:
        return 0.0, 0.0

    # Calculate average and max from results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)

    avg_distance = total_distance / total_points if total_points > 0 else 0
    return round(avg_distance, 2), round(max_distance, 2)
