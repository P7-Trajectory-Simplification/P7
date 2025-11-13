from concurrent.futures import ProcessPoolExecutor
import numpy as np
from algorithms.great_circle_math import great_circle_distance
from classes.route import Route
from classes.vessel_log import VesselLog
        
def find_simplified_point_vectorized(raw_times: np.ndarray, simplified_times: np.ndarray) -> np.ndarray:
    '''Find which point of the simplified route each raw point belongs to (vectorized).
    The code assumes that both raw_times and simplified_times are sorted arrays of timestamps, 
    and uses numpy for efficient computation and binary search in C instead of looping through everything in Python.
    Returns an array of simplified point indices for each raw point.'''
    #Find closest simplified point for each raw point (vectorized)
    idx = np.searchsorted(simplified_times, raw_times, side="left")

    #Handle out-of-bound indices (replace with nearest valid)
    idx[idx == len(simplified_times)] = len(simplified_times) - 1
    idx[idx == 0] = 0

    #For points that fall between two simplified timestamps, choose closer one
    prev_idx = np.clip(idx - 1, 0, len(simplified_times) - 1)
    next_idx = np.clip(idx, 0, len(simplified_times) - 1)

    prev_diff = np.abs(raw_times - simplified_times[prev_idx])
    next_diff = np.abs(raw_times - simplified_times[next_idx])

    closest_idx = np.where(prev_diff < next_diff, prev_idx, next_idx)
    
    return closest_idx


def sed_single_route_vectorized(raw_route: Route, simplified_route: Route) -> tuple[float, float, int]:
    '''Compute SED for a single route (vectorized).
    Using vectorized simplified point lookup and parallel great-circle distance computation.
    Returns average distance, max distance, and count of points.'''

    #Return average distance, max distance, count as 0, if either route is empty.
    if len(raw_route.trajectory) == 0 or len(simplified_route.trajectory) == 0:
        return 0.0, 0.0, 0
    
    #Convert to numpy arrays for vectorized operations
    raw_latlon = np.array([p.get_coords() for p in raw_route.trajectory])
    simplified_latlon = np.array([p.get_coords() for p in simplified_route.trajectory])
    raw_times = np.array([p.ts.timestamp() for p in raw_route.trajectory])
    simplified_times = np.array([p.ts.timestamp() for p in simplified_route.trajectory])

    #Gets an array of simplified point indices for each raw point
    point_idx = find_simplified_point_vectorized(raw_times, simplified_times)
    simplified_point = simplified_latlon[point_idx]

    #Compute distances using great_circle_distance
    #Could potentially eliminate the loop, if great_circle_distance is vectorized (could accept arrays)
    distances = np.array([
        great_circle_distance(simplified_point[i], raw_latlon[i])
        

        for i in range(len(raw_latlon))
    ])
    return np.mean(distances), np.max(distances), len(distances)

def sed_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    '''Calculate the average Point to simplified point Euclidean distance between two trajectories
    and the maximum Point to simplified point Euclidean distance between two trajectories.

    Returns:
        tuple with floats: The average SED between the two trajectories and the max distance.
    '''
    #Use multiprocessing to compute SED for each route in parallel
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(sed_single_route_vectorized, raw_data_routes, simplified_routes))

    #Calculate average and max from results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)
    avg_distance = total_distance / total_points if total_points > 0 else 0
    return round(avg_distance, 2), round(max_distance, 2)