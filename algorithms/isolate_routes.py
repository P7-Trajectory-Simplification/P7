from classes.route import Route
from classes.vessel_log import VesselLog


def is_vessel_static(vessel_logs: list[VesselLog]) -> bool:
    latitudes = [log.lat for log in vessel_logs]
    longitudes = [log.lon for log in vessel_logs]
    if (
        max(latitudes) - min(latitudes) < 0.001
        and max(longitudes) - min(longitudes) < 0.001
    ):
        return True
    return False


def isolate_trajectories(logs: list[VesselLog]) -> list[list[VesselLog]]:
    if not logs:
        return []

    trajectories = []
    current_trajectory = [logs[0]]  # Add the first point to a trajectory

    # Loops through all logs and determines if the time gap between the points is small enough for it to be the same route.
    for i in range(1, len(logs)):
        if (
            logs[i].ts - logs[i - 1].ts
        ).total_seconds() > 86400 * 2:  # 86400 seconds in a day
            trajectories.append(current_trajectory)
            current_trajectory = [logs[i]]
        else:
            current_trajectory.append(logs[i])

    trajectories.append(current_trajectory)
    return trajectories


def is_vessel_static(vessel_logs: list[VesselLog]) -> bool:
    latitudes = [log.lat for log in vessel_logs]
    longitudes = [log.lon for log in vessel_logs]
    if (
        max(latitudes) - min(latitudes) < 0.001
        and max(longitudes) - min(longitudes) < 0.001
    ):
        return True
    return False


def isolate_routes(logs: list[VesselLog]) -> list[Route]:
    """
    Divide raw data into dedicated routes, so data points with large time gaps in between are not connected.

    Parameters
    ----------
    logs: a list of VesselLog's
        Raw data which needs to be split

    Returns
    ----------
    A list of dicts with routes and a buffer for the squish algorithm
    """
    if not logs:
        return [Route()]

    routes = []
    current_route = [logs[0]]  # Add the first point to a route

    # Loops through all logs and determines if the time gap between the points is small enough for it to be the same route.
    for i in range(1, len(logs)):
        if (
            logs[i].ts - logs[i - 1].ts
        ).total_seconds() > 86400 * 2:  # 86400 seconds in a day
            routes.append(Route(current_route))
            current_route = [logs[i]]
        else:
            current_route.append(logs[i])

    routes.append(Route(current_route))
    return routes


# TODO global variables are yucky but this works. They could be put into a class alongside assign_routes.
last_time = {}  # maps IMOs to the timestamp of the last log we got from that vessel
current_route = {}  # maps IMOs to the ID of the route that vessel is currently on
route_count = 0  # counts how many routes exist


def assign_routes(
    logs: list[VesselLog], threshold: int | float = 86400 * 2
) -> dict[int, list[VesselLog]]:
    """Online implementation of isolate_routes.
    Places the points from the given list into routes and ensures all routes have a unique ID.
    Assigns a new route to a vessel if enough time has passed since the last point was recorded.

    Parameters
    ----------
    packed_logs: iterable of (imo, VesselLog) pairs.
        Each item in the given iterable will be assigned a route.

    threshold: int or float.
        If two consecutive logs from the same vessel occur with this many seconds between them,
        they will be placed in different routes, with a new route being created to support that.

    Returns
    ----------
    A dictionary mapping route IDs to lists of VesselLogs
    in the order they should be considered for the routes they are part of.
    """
    global route_count
    routes = {}
    for log in logs:
        imo = log.imo
        if (
            imo not in current_route
            or (log.ts - last_time[imo]).total_seconds() > threshold
        ):
            # if there's no route registered for the given vessel identifier, prepare one for it and increment the route_count
            current_route[imo] = route_count
            routes[route_count] = []
            route_count += 1
        elif current_route[imo] not in routes:
            # if this is the first log we get from this vessel but we already know its route, prepare a list for that vessel's logs
            routes[current_route[imo]] = []
        # we have a route registered for the vessel and a list we can append to, so we do that and update when we last heard from that vessel
        routes[current_route[imo]].append(log)
        last_time[imo] = log.ts
    return routes
