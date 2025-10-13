
from datetime import timedelta
from vessel_log import VesselLog


def isolate_routes(logs: list[VesselLog]) -> list[list[VesselLog]]:
    if not logs:
        return []

    routes = []
    current_route = [logs[0]]

    for i in range(1, len(logs)):
        if (logs[i].ts - logs[i - 1].ts).total_seconds() > 86400*2:  # 86400 seconds in a day
            routes.append(current_route)
            current_route = [logs[i]]
        else:
            current_route.append(logs[i])

    routes.append(current_route)
    return routes
    

