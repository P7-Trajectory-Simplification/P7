from typing import Tuple
import numpy as np
from algorithms.great_circle_math import great_circle_distance, point_to_great_circle
from classes.vessel_log import VesselLog

import numpy as np

EARTH_RADIUS_M = 6371000  # mean Earth radius in meters

def latlon_to_ecef(lat_deg: float, lon_deg: float):
    """Convert lat/lon in degrees to ECEF (x,y,z)."""
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    x = EARTH_RADIUS_M * np.cos(lat) * np.cos(lon)
    y = EARTH_RADIUS_M * np.cos(lat) * np.sin(lon)
    z = EARTH_RADIUS_M * np.sin(lat)
    return np.array([x, y, z])

def euclidean_point_to_point(p1_latlon, p2_latlon):
    P1 = latlon_to_ecef(p1_latlon[0], p1_latlon[1])
    P2 = latlon_to_ecef(p2_latlon[0], p2_latlon[1])
    return np.linalg.norm(P1 - P2)

def euclidean_point_to_segment(A_latlon, B_latlon, P_latlon):
    A = latlon_to_ecef(A_latlon[0], A_latlon[1])
    B = latlon_to_ecef(B_latlon[0], B_latlon[1])
    P = latlon_to_ecef(P_latlon[0], P_latlon[1])

    AB = B - A
    AP = P - A

    denom = np.dot(AB, AB)
    if denom == 0:
        return np.linalg.norm(P - A)  # A and B identical

    t = np.dot(AP, AB) / denom
    t = np.clip(t, 0, 1)

    closest = A + t * AB
    return np.linalg.norm(P - closest)


def find_nearest_simplified_idx_vectorized(
    raw_times: np.ndarray, simp_times: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Given sorted raw and simplified timestamps,
    return arrays (left_indices, right_indices) for each raw point.
    Ensures:
        left_idx < right_idx
        both in valid ranges
    """

    # For each raw timestamp find the index where it would be inserted in the simplified timestamps
    idx = np.searchsorted(simp_times, raw_times, side="left")

    # Clamp raw timestamps to valid interval [1, len-1]
    idx = np.clip(idx, 1, len(simp_times) - 1)

    # Get the index of the previous simplified timestamp
    left_idx = idx - 1
    right_idx = idx

    return left_idx, right_idx


def ped_single_route_vectorized(
    raw_route: list[VesselLog], simplified_route: list[VesselLog], math: dict
) -> tuple[float, float, int]:
    """PED: for each raw point, find the simplified point
    with the closest previous timestamp and compute the point to great-circle distance.

    Returns:
        (mean_distance_m, max_distance_m, number_of_raw_points)
    """

    # Handle edge case of empty routes
    if len(raw_route) == 0 or len(simplified_route) == 0:
        return 0.0, 0.0, 0

    # Convert coords + times to arrays
    raw_latlon = np.array([p.get_coords() for p in raw_route])
    simp_latlon = np.array([p.get_coords() for p in simplified_route])

    raw_times = np.array([p.ts.timestamp() for p in raw_route])
    simp_times = np.array([p.ts.timestamp() for p in simplified_route])

    n_raw = len(raw_latlon)
    n_simp = len(simp_latlon)

    if n_raw == 0 or n_simp == 0:
        return 0.0, 0.0, 0

    # Case: only one simplified point -> PED is point-to-point distance
    if n_simp == 1:
        distances = np.array(
            [
                euclidean_point_to_point(simp_latlon[0], raw_latlon[i])
                for i in range(n_raw)
            ]
        )
        if len(distances) == 0:
            return 0.0, 0.0, 0
        return float(np.mean(distances)), float(np.max(distances)), len(distances)

    # Find nearest simplified time index for each raw point, finds the preceding point
    left_idx, rigth_idx = find_nearest_simplified_idx_vectorized(raw_times, simp_times)

    # Collect matched simplified coords
    left_points = simp_latlon[left_idx]
    right_points = simp_latlon[rigth_idx]

    # Compute distances vectorized
    distances = []
    for i in range(n_raw):
        A = left_points[i]
        B = right_points[i]
        P = raw_latlon[i]

        # Handle segment where (A == B)
        if np.allclose(A, B):
            d = euclidean_point_to_point(A, P)
        else:
            d = euclidean_point_to_segment(A, B, P)

        if not np.isnan(d) and d >= 0:
            distances.append(d)

    if not distances:
        return 0.0, 0.0, 0

    distances = np.array(distances)
    return float(np.mean(distances)), float(np.max(distances)), len(distances)


def ped_results(
    raw_data_routes: dict[int, list[VesselLog]],
    simplified_routes: dict[int, list[VesselLog]],
    math: dict,
) -> tuple[float, float]:
    """Calculate the average Point to segment Euclidean distance between two trajectories and the maximum Point to segment Euclidean distance between two trajectories.

    Returns:
        tuple of floats: The average PED between the two trajectories and the max distance.
    """

    # Calculate PED for each (raw route, simplified route) pair
    # NOTE that raw_data_routes and simplified_routes will always have the same keys
    results = []
    for key in raw_data_routes:
        raw_route = raw_data_routes[key]
        # If simplified route is missing, use empty list
        simp_route = simplified_routes.get(key, [])

        avg_d, max_d, count = ped_single_route_vectorized(raw_route, simp_route, math)

        if count > 0:  # ignore empty/invalid routes
            results.append((avg_d, max_d, count))

    # If no results were computed, return zeros, happens if no matching routes or all empty
    if not results:
        return 0.0, 0.0

    # Aggregate results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_dist for _, max_dist, _ in results)

    avg_distance = total_distance / total_points if total_points > 0 else 0

    return round(avg_distance, 2), round(max_distance, 2)
