from concurrent.futures import ProcessPoolExecutor

import numpy as np
from algorithms.great_circle_math import point_to_great_circle
from classes.route import Route
from classes.vessel_log import VesselLog

def find_segment(point: VesselLog, trajectory: list[VesselLog]) -> tuple[VesselLog, VesselLog] | None: 
    """Find the segment in the trajectory whose time interval is closest to the point's time."""
    for i in range(len(trajectory) - 1):
        start = trajectory[i]
        end = trajectory[i + 1]
        # Find time difference between point_time and the segment's interval
        if start.ts <= point.ts <= end.ts:
            return (start, end)
    
    #Print to inform that the point is outside the segment time interval and a segment therefore hasn't been chosen.
    return None
        
def find_segments_vectorized(raw_times, simplified_times):
    #Find insertion indices — which segment each raw point belongs to
    idx = np.searchsorted(simplified_times, raw_times, side="right") - 1
    idx = np.clip(idx, 0, len(simplified_times) - 2)  #keep within valid range
    return idx

def ped_single_route_vectorized(raw_route: Route, simplified_route: Route):
    raw_latlon = np.array([p.get_coords() for p in raw_route.trajectory])
    simplified_latlon = np.array([p.get_coords() for p in simplified_route.trajectory])
    raw_times = np.array([p.ts.timestamp() for p in raw_route.trajectory])
    simplified_times = np.array([p.ts.timestamp() for p in simplified_route.trajectory])

    seg_idx = find_segments_vectorized(raw_times, simplified_times)
    starts = simplified_latlon[seg_idx]
    ends = simplified_latlon[seg_idx + 1]

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
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(ped_single_route_vectorized, raw_data_routes, simplified_routes))

    # Calculate average and max from results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)

    avg_distance = total_distance / total_points if total_points > 0 else 0
    return round(avg_distance, 2), round(max_distance, 2)
