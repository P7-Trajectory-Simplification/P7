from concurrent.futures import ProcessPoolExecutor
import numpy as np
from algorithms.great_circle_math import great_circle_distance
from classes.route import Route
from classes.vessel_log import VesselLog



def find_nearest_simplified_idx_vectorized(raw_times: np.ndarray, simp_times: np.ndarray) -> np.ndarray:
    """
    Given raw timestamps and simplified timestamps (sorted),
    return for each raw time the index of the *nearest* simplified timestamp.
    """
    # Insertion positions
    idx = np.searchsorted(simp_times, raw_times)

    # Clamp to valid interval [1, len-1]
    idx = np.clip(idx, 1, len(simp_times) - 1)

    # Compare left vs right neighbor
    left = idx - 1
    right = idx

    choose_right = (
        np.abs(raw_times - simp_times[right]) <
        np.abs(raw_times - simp_times[left])
    )

    nearest_idx = np.where(choose_right, right, left)

    return nearest_idx

def ped_single_route_vectorized(raw_route: Route, simplified_route: Route) -> tuple[float, float, int]:
    """
    PED: for each raw point, find the simplified point 
    with the closest timestamp and compute the great-circle distance.

    Returns:
        (mean_distance_m, max_distance_m, number_of_raw_points)
    """

    if len(raw_route.trajectory) == 0 or len(simplified_route.trajectory) == 0:
        return 0.0, 0.0, 0

    #Convert coords + times to arrays
    raw_latlon = np.array([p.get_coords() for p in raw_route.trajectory])
    simp_latlon = np.array([p.get_coords() for p in simplified_route.trajectory])

    raw_times = np.array([p.ts.timestamp() for p in raw_route.trajectory])
    simp_times = np.array([p.ts.timestamp() for p in simplified_route.trajectory])

    #Find nearest simplified time index for each raw point
    nearest_idx = find_nearest_simplified_idx_vectorized(raw_times, simp_times)

    #Collect matched simplified coords
    nearest_points = simp_latlon[nearest_idx]

    #Compute distances vectorized
    distances = np.array([
        great_circle_distance(raw_latlon[i], nearest_points[i])
        for i in range(len(raw_latlon))
    ])

    return float(np.mean(distances)), float(np.max(distances)), len(distances)

def ped_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    """
    Calculate average and max PED across multiple routes.
    """

    results = [
        ped_single_route_vectorized(raw, simp)
        for raw, simp in zip(raw_data_routes, simplified_routes)
    ]

    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)

    avg_distance = total_distance / total_points if total_points > 0 else 0

    return round(avg_distance, 2), round(max_distance, 2)
