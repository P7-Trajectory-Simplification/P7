import numpy as np
from algorithms.great_circle_math import (
    great_circle_distance,
    predict_sphere_movement,
    get_final_bearing,
    EARTH_RADIUS_METERS,
)
from classes.route import Route
from classes.vessel_log import VesselLog

prediction_startpoint = None
prediction_endpoint = None


def dead_reckoning(trajectory: list[VesselLog], tolerance: int = 100) -> list[VesselLog]:
    '''
    Simplifies a given set of points using the Dead-Reckoning algorithm.

    Parameters
    ----------
    trajectory: A list of VesselLog's
        The Datapoints that have to be simplified
    tolerance: Int (default value = 100)
        Max allowed distance from predicted point to received point in meters

    Returns
    ----------
    A list of VesselLog's
        The simplified set of points.
    '''

    global prediction_startpoint
    global prediction_endpoint

    if len(trajectory) < 2:
        return trajectory
    elif len(trajectory) == 2:
        prediction_startpoint = trajectory[-2]
        prediction_endpoint = trajectory[-1]
        return trajectory

    next_newest_point = trajectory[-2]
    newest_point = trajectory[-1]

    error = reckon(prediction_startpoint, prediction_endpoint, newest_point)

    if np.abs(error) > tolerance:
        # if the predicted point is further than we tolerate, reset prediction points
        prediction_startpoint = next_newest_point
        prediction_endpoint = newest_point
    else:
        # if the predicted point is close enough, we don't need the next newest point anymore and can safely exclude it
        del trajectory[-2]
    return trajectory

# Helper function for squish reckoning
def reckon(point_a: VesselLog, point_b: VesselLog, point_c: VesselLog) -> float:
    '''Given three points with latitude, longitude, and timestamp, return the distance between point c and point c as predicted by point a and b via dead reckoning

    Parameters
    ----------
    point_a : _VesselLog_
        The log representing the first point.
    point_b : _VesselLog_
        The log representing the second point. It is this point we attribute the returned value distance to.
    point_c : _VesselLog_
        The log representing the point to predict.
    '''
    latlon_a = point_a.get_coords()
    latlon_b = point_b.get_coords()

    # find distance from A to B
    distance = great_circle_distance(latlon_a, latlon_b, radius=EARTH_RADIUS_METERS)
    time_delta = (point_b.ts - point_a.ts).total_seconds()
    velocity = 0  # velocity in m/s
    if time_delta != 0:
        # avoid dividing by 0 when the points have the same timestamp
        velocity = distance / time_delta
    # find bearing at B
    prediction_bearing = get_final_bearing(latlon_a, latlon_b)
    # find time difference between B and C and multiply by the velocity we found
    prediction_time_delta = (point_c.ts - point_b.ts).total_seconds()
    prediction_distance = velocity * prediction_time_delta
    # now predict where C should be
    c_predicted = predict_sphere_movement(
        latlon_b,
        prediction_distance,
        prediction_bearing,
        radius=EARTH_RADIUS_METERS,
    )
    # return distance from predicted C to actual C
    return great_circle_distance(
        c_predicted, point_c.get_coords(), radius=EARTH_RADIUS_METERS
    )

def run_dr(route: Route, params: dict) -> Route:
    simplified_trajectory = []
    for vessel_log in route.trajectory:
        simplified_trajectory.append(vessel_log)
        simplified_trajectory = dead_reckoning(simplified_trajectory, params["tolerance"])

    return Route(simplified_trajectory)