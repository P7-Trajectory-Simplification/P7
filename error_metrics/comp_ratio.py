from classes.vessel_log import VesselLog


def comp_ratio_results(
    raw_data_routes: dict[int, list[VesselLog]],
    simplified_routes: dict[int, list[VesselLog]],
) -> float:
    """Calculate the compression ratio between two trajectories."""
    total_raw_points = 0
    total_simplified_points = 0

    # Count total points in raw and simplified routes
    for key, raw_route in raw_data_routes.items():
        simplified_route = simplified_routes[key]
        total_raw_points += len(raw_route)
        total_simplified_points += len(simplified_route)

    return comp_ratio(total_raw_points, total_simplified_points)


def comp_ratio(raw_data_num_points: int, simplified_num_points: int) -> float:
    """Calculate the compression ratio between two trajectories."""
    if raw_data_num_points == 0:
        return 0.0  # Avoid division by zero

    # Calculate compression ratio (not as a percentage!)
    compression_ratio = simplified_num_points / raw_data_num_points
    return round(compression_ratio, 4)
