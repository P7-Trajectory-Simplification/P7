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
    print("Point time is outside the segment time interval.")
    return None
        
def ped_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> tuple[float, float]:
    """Calculate the average Point to segment Euclidean distance between two trajectories and the maximum Point to segment Euclidean distance between two trajectories.

    Returns:
        tuple of floats: The average PED between the two trajectories and the max distance.
    """
    max_distance = 0
    total_distance = 0
    count = 0

    for i, raw_route in enumerate(raw_data_routes):
        simplified_route = simplified_routes[i]
        for point in raw_route.trajectory:
            segment = find_segment(point, simplified_route.trajectory)
            if segment is not None:
                start_seg, end_seg = segment
                distance = point_to_great_circle(start_seg.get_coords(), end_seg.get_coords(), point.get_coords()) #ped((point.lat.get_coords(), point.lon.get_coords()), (start_seg[0], start_seg[1]), (end_seg[0], end_seg[1]))
                total_distance += distance
                count += 1
            if distance > max_distance:
                    max_distance = distance

    if count == 0:
        return 0,0  # both average and max are zero


    avg_distance = total_distance / count
    return round(avg_distance, 2), round(max_distance, 2)
