import numpy as np

from classes.vessel_log import VesselLog

EARTH_RADIUS_M = 6371000

def latlon_to_ecef(lat_deg, lon_deg):
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    x = EARTH_RADIUS_M * np.cos(lat) * np.cos(lon)
    y = EARTH_RADIUS_M * np.cos(lat) * np.sin(lon)
    z = EARTH_RADIUS_M * np.sin(lat)
    return np.array([x, y, z])

def euclidean_point_to_point(P1_latlon, P2_latlon):
    P1 = latlon_to_ecef(P1_latlon[0], P1_latlon[1])
    P2 = latlon_to_ecef(P2_latlon[0], P2_latlon[1])
    return np.linalg.norm(P1 - P2)

def interpolate_euclidean(A_latlon, B_latlon, alpha):
    A = latlon_to_ecef(A_latlon[0], A_latlon[1])
    B = latlon_to_ecef(B_latlon[0], B_latlon[1])

    P = A + alpha * (B - A)  # linear interp in 3D

    # convert back to lat/lon
    x, y, z = P
    lat = np.degrees(np.arctan2(z, np.sqrt(x*x + y*y)))
    lon = np.degrees(np.arctan2(y, x))
    return np.array([lat, lon])

def interpolate_simplified_points_vectorized(raw_times, simp_times, simp_latlon):
    idx = np.searchsorted(simp_times, raw_times, side="right") - 1
    idx = np.clip(idx, 0, len(simp_times) - 2)

    t0 = simp_times[idx]
    t1 = simp_times[idx + 1]
    dt = t1 - t0

    zero_dt = dt == 0
    alpha = np.zeros_like(dt, dtype=float)
    valid = ~zero_dt
    alpha[valid] = (raw_times[valid] - t0[valid]) / dt[valid]
    alpha = np.clip(alpha, 0.0, 1.0)

    result = np.zeros((len(raw_times), 2))
    for i in range(len(raw_times)):
        result[i] = interpolate_euclidean(
            simp_latlon[idx[i]],
            simp_latlon[idx[i] + 1],
            alpha[i],
        )

    return result

def sed_single_route_vectorized(raw_route, simplified_route, math):
    if len(raw_route) == 0 or len(simplified_route) == 0:
        return 0.0, 0.0, 0

    raw_latlon = np.array([p.get_coords() for p in raw_route])
    simp_latlon = np.array([p.get_coords() for p in simplified_route])
    raw_times = np.array([p.ts.timestamp() for p in raw_route])
    simp_times = np.array([p.ts.timestamp() for p in simplified_route])

    interp_points = interpolate_simplified_points_vectorized(
        raw_times, simp_times, simp_latlon
    )

    distances = [
        euclidean_point_to_point(interp_points[i], raw_latlon[i])
        for i in range(len(raw_latlon))
    ]

    return np.mean(distances), np.max(distances), len(distances)

def sed_results(
    raw_data_routes: dict[int, list[VesselLog]],
    simplified_routes: dict[int, list[VesselLog]],
    math: dict,
) -> tuple[float, float]:
    """Calculate the average Point to simplified point Euclidean distance between two trajectories
    and the maximum Point to simplified point Euclidean distance between two trajectories.

    Returns:
        tuple with floats: The average SED between the two trajectories and the max distance.
    """
    results = [
        sed_single_route_vectorized(raw_data_routes[k], simplified_routes[k], math)
        for k in raw_data_routes
    ]
    # If no results were computed, return zeros, happens if no matching routes or all empty
    if not results:
        return 0.0, 0.0

    # Calculate average and max from results
    total_distance = sum(avg * count for avg, _, count in results)
    total_points = sum(count for _, _, count in results)
    max_distance = max(max_d for _, max_d, _ in results)

    avg_distance = total_distance / total_points if total_points > 0 else 0
    return round(avg_distance, 2), round(max_distance, 2)
