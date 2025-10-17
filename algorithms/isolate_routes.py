
from datetime import timedelta
from vessel_log import VesselLog



def isolate_routes(logs: list[VesselLog]) -> list[dict['route':list[VesselLog], 'squish_buff': []]]:
    '''
    Divide raw data into dedicated routes, so data points with large time gaps in between are not connected.
    
    Parameters
    ----------
    logs: a list of VesselLog's
        Raw data which needs to be split
    
    Returns
    ----------
    A list of dicts with routes and a buffer for the squish algorithm
    '''
    if not logs:
        return []

    routes = []
    current_route = [logs[0]] #Add the first point to a route

    #Loops through all logs and determines if the time gap between the points is small enough for it to be the same route.
    for i in range(1, len(logs)):
        if (logs[i].ts - logs[i - 1].ts).total_seconds() > 86400*2:  # 86400 seconds in a day
            routes.append({'route': current_route, 'squish_buff': []})
            current_route = [logs[i]]
        else:
            current_route.append(logs[i])


    routes.append({'route': current_route, 'squish_buff': []})
    return routes
    

