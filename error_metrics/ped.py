from concurrent.futures import ProcessPoolExecutor
import numpy as np
from algorithms.great_circle_math import point_to_great_circle
from classes.route import Route
from classes.vessel_log import VesselLog



def find_nearest_simplified_idx_vectorized(raw_times: np.ndarray, simp_times: np.ndarray) -> np.ndarray:
    '''Given raw timestamps and simplified timestamps (sorted),
    return for each raw time the index of the previous simplified timestamp.
    '''
    #For each raw timestamp find the index where it would be inserted in the simplified timestamps
    idx = np.searchsorted(simp_times, raw_times)

    #Clamp raw timestamps to valid interval [1, len-1]
    idx = np.clip(idx, 1, len(simp_times) - 1)

    #Get the index of the previous simplified timestamp
    left = idx - 1

    nearest_idx = left

    return nearest_idx

def ped_single_route_vectorized(raw_route: Route, simplified_route: Route) -> tuple[float, float, int]:
    '''PED: for each raw point, find the simplified point 
    with the closest previous timestamp and compute the point to great-circle distance.

    Returns:
        (mean_distance_m, max_distance_m, number_of_raw_points)
    '''

    #Handle edge case of empty routes
    if len(raw_route.trajectory) == 0 or len(simplified_route.trajectory) == 0:
        return 0.0, 0.0, 0

    #Convert coords + times to arrays
    raw_latlon = np.array([p.get_coords() for p in raw_route.trajectory])
    simp_latlon = np.array([p.get_coords() for p in simplified_route.trajectory])

    raw_times = np.array([p.ts.timestamp() for p in raw_route.trajectory])
    simp_times = np.array([p.ts.timestamp() for p in simplified_route.trajectory])

    #Find nearest simplified time index for each raw point, finds the preceding point
    nearest_idx = find_nearest_simplified_idx_vectorized(raw_times, simp_times)

    #Collect matched simplified coords
    nearest_points = simp_latlon[nearest_idx]

    #Compute distances vectorized
    distances = np.array([
        point_to_great_circle(nearest_points[i], nearest_points[i+1], raw_latlon[i])
        for i in range(len(raw_latlon))
    ])

    return float(np.mean(distances)), float(np.max(distances)), len(distances)

def ped_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    '''Calculate the average Point to segment Euclidean distance between two trajectories and the maximum Point to segment Euclidean distance between two trajectories.

    Returns:
        tuple of floats: The average PED between the two trajectories and the max distance.
    '''

    #Calculate PED for each route pair
    results = [
        ped_single_route_vectorized(raw, simplified)
        for raw, simplified in zip(raw_data_routes, simplified_routes)
    ]

    #Aggregate results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_dist for _, max_dist, _ in results)

    avg_distance = total_distance / total_points if total_points > 0 else 0

    return round(avg_distance, 2), round(max_distance, 2)
