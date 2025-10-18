import numpy as np
from algorithms.great_circle_math import great_circle_distance, predict_sphere_movement, get_final_bearing, EARTH_RADIUS_METERS
from classes.route import Route
from classes.vessel_log import VesselLog

prediction_startpoint = None
prediction_endpoint = None


def dead_reckoning(points: list[VesselLog], tolerance: int = 100) -> list[VesselLog]:
    '''
    Simplifies a given set of points using the Dead-Reckoning algorithm.
    
    Parameters
    ----------
    points: A list of VesselLog's
        The Datapoints that have to be simplified
    tolerance: Int (default value = 100)
        Max allowed distance from predicted point to received point in meters

    Returns
    ----------
    A list of VesselLog's
        The simplified set of points.
    '''

    if len(points) < 2:
        return points
    elif len(points) == 2:
        prediction_startpoint = points[-2]
        prediction_endpoint = points[-1]
        return points

    next_newest_point = points[-2]
    newest_point = points[-1]

    # (L1) find initial geodesic
    distance = great_circle_distance(
        prediction_startpoint.get_coords(),
        prediction_endpoint.get_coords(),
        radius=EARTH_RADIUS_METERS,
    )
    time_delta = (prediction_endpoint.ts - prediction_startpoint.ts).total_seconds()
    velocity = 0  # velocity in m/s
    if time_delta != 0:
        # avoid dividing by 0 when the points have the same timestamp
        velocity = distance / time_delta

    # find starting point for reckoning (end of initial geodesic)
    latlon_startpoint = prediction_startpoint.get_coords()
    latlon_endpoint = prediction_endpoint.get_coords()
    # find bearing
    prediction_bearing = get_final_bearing(latlon_startpoint, latlon_endpoint)
    # find time difference between starting point and next potential point and multiply by the velocity we found
    prediction_time_delta = (newest_point.ts - prediction_endpoint.ts).total_seconds()
    prediction_distance = velocity * prediction_time_delta
    # now predict where the next point should be
    latlon_predicted = predict_sphere_movement(
        latlon_endpoint,
        prediction_distance,
        prediction_bearing,
        radius=EARTH_RADIUS_METERS,
    )
    # compare difference between predicted next point and potential next point to tolerance
    error = great_circle_distance(
        latlon_predicted, newest_point.get_coords(), radius=EARTH_RADIUS_METERS
    )
    if np.abs(error) > tolerance:
        # if the predicted point is further than we tolerate, reset prediction points
        prediction_startpoint = next_newest_point
        prediction_endpoint = newest_point
    else:
        # if the predicted point is close enough, we don't need the next newest point anymore and can safely exclude it
        del points[-2]
    return points


def run_dr(route: Route) -> Route:
    simplified_trajectory = []
    for vessel_log in route.trajectory:
        simplified_trajectory.append(vessel_log)
        simplified_trajectory = dead_reckoning(simplified_trajectory, tolerance=2000)

    return Route(simplified_trajectory)