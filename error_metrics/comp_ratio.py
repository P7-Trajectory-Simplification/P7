from classes.route import Route

def comp_ratio_results(raw_data_routes: list[Route], simplified_routes: list[Route]) -> float:
    """Calculate the compression ratio between two trajectories."""
    total_raw_points = 0
    total_simplified_points = 0

    # Count total points in raw and simplified routes
    for i, raw_route in enumerate(raw_data_routes):
        simplified_route = simplified_routes[i]
        total_raw_points += len(raw_route.trajectory)
        total_simplified_points += len(simplified_route.trajectory)

    if total_raw_points == 0:
        return 0.0  # Avoid division by zero

    # Calculate compression ratio in percentage
    compression_ratio = total_simplified_points / total_raw_points * 100
    return round(compression_ratio, 4)