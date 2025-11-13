from concurrent.futures import ProcessPoolExecutor

import numpy as np
from algorithms.great_circle_math import point_to_great_circle
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

def ped_single_route_vectorized(raw_route: Route, simplified_route: Route) -> tuple[float, float, int]:
    '''Compute the PED for all points in a single route — 
    using vectorized segment lookup and parallel great-circle distance computation.
    And return average distance, max distance, and lenght of the simplified route'''

    #Convert to numpy arrays for vectorized operations
    raw_latlon = np.array([p.get_coords() for p in raw_route.trajectory])
    simplified_latlon = np.array([p.get_coords() for p in simplified_route.trajectory])
    raw_times = np.array([p.ts.timestamp() for p in raw_route.trajectory])
    simplified_times = np.array([p.ts.timestamp() for p in simplified_route.trajectory])

    #Gets an array of segment start indices for each raw point and creates start and end point arrays
    seg_idx = find_segments_vectorized(raw_times, simplified_times)
    starts = simplified_latlon[seg_idx]
    ends = simplified_latlon[seg_idx + 1]

    #Compute distances using point_to_great_circle
    distances = np.array([
        point_to_great_circle(starts[i], ends[i], raw_latlon[i])
        for i in range(len(raw_latlon))
    ])
    return np.mean(distances), np.max(distances), len(distances)

def ped_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    """Calculate the average Point to segment Euclidean distance between two trajectories and the maximum Point to segment Euclidean distance between two trajectories.

    Returns:
        tuple of floats: The average PED between the two trajectories and the max distance.
    """
    #Use multiprocessing to compute PED for each route in parallel
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(ped_single_route_vectorized, raw_data_routes, simplified_routes))

    #Calculate average and max from results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)
    avg_distance = total_distance / total_points if total_points > 0 else 0
    return round(avg_distance, 2), round(max_distance, 2)
