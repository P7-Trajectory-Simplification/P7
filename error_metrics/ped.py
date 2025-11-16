from concurrent.futures import ProcessPoolExecutor

import numpy as np
from algorithms.great_circle_math import great_circle_distance, point_to_great_circle
from classes.route import Route
from classes.vessel_log import VesselLog
        
def find_segments_vectorized(raw_times: np.ndarray, simplified_times: np.ndarray) -> np.ndarray:
    '''Find which segment of the simplified route each raw point belongs to (vectorized).
    The code assumes that both raw_times and simplified_times are sorted arrays of timestamps, 
    and uses numpy for efficient computation and binary search in C instead of looping through everything in Python.
    Returns an array of segment start indices for each raw point.'''
    #Find insertion indices, i.e. which segment each raw point belongs to, -1 is used to only get the start of the segment
    idx = np.searchsorted(simplified_times, raw_times, side="right") - 1
    #Handle out-of-bound indices (replace with nearest valid), -2 is the last valid start index
    idx = np.clip(idx, 0, len(simplified_times) - 2)  
    return idx

def ped_single_route_vectorized(raw_route: Route, simplified_route: Route):
    """
    Nearest-neighbor PED: for each raw point, find the simplified point 
    with the closest timestamp and compute the great-circle distance.
    Returns: (mean_distance, max_distance, count)
    """

    if len(raw_route.trajectory) == 0 or len(simplified_route.trajectory) == 0:
        return 0.0, 0.0, 0

    # --- Convert raw and simplified to arrays ---
    raw_latlon = np.array([p.get_coords() for p in raw_route.trajectory])
    simp_latlon = np.array([p.get_coords() for p in simplified_route.trajectory])

    raw_times = np.array([p.ts.timestamp() for p in raw_route.trajectory])
    simp_times = np.array([p.ts.timestamp() for p in simplified_route.trajectory])

    # --- For each raw time, find nearest simplified timestamp ---
    # searchsorted gives insertion position
    idx = np.searchsorted(simp_times, raw_times)

    # clamp to valid range
    idx = np.clip(idx, 1, len(simp_times) - 1)

    # neighbor indices
    left = idx - 1
    right = idx

    # determine which neighbor is closer
    choose_right = (np.abs(raw_times - simp_times[right])
                    < np.abs(raw_times - simp_times[left]))

    nearest_idx = np.where(choose_right, right, left)

    # --- Collect nearest neighbor coords ---
    nearest_points = simp_latlon[nearest_idx]

    # --- Vectorized great-circle distances over all pairs ---
    distances = np.array([
        great_circle_distance(raw_latlon[i], nearest_points[i])
        for i in range(len(raw_latlon))
    ])

    return float(np.mean(distances)), float(np.max(distances)), len(distances)

def ped_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    """Calculate the average Point to segment Euclidean distance between two trajectories and the maximum Point to segment Euclidean distance between two trajectories.

    Returns:
        tuple of floats: The average PED between the two trajectories and the max distance.
    """
    #Use multiprocessing to compute PED for each route in parallel
    results = [ped_single_route_vectorized(r, s) for r, s in zip(raw_data_routes, simplified_routes)]


    #Calculate average and max from results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)
    avg_distance = total_distance / total_points if total_points > 0 else 0
    return round(avg_distance, 2), round(max_distance, 2)
