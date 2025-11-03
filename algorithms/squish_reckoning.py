import numpy as np
from algorithms.great_circle_math import (
    great_circle_distance,
    predict_sphere_movement,
    get_final_bearing,
    EARTH_RADIUS_METERS,
)
from algorithms.dead_reckoning import reckon
from classes.route import Route
from classes.vessel_log import VesselLog

# memoization of VesselLogs' scores. Remember to delete logs that aren't in the buffer!
scores = {}


def squish_reckoning(
    points: list[VesselLog], buffer_size: int = 100
) -> list[VesselLog]:
    if len(points) < 3:
        # nothing to do, and buffer size shouldn't be considered since we always want the first and last point
        return points

    if (next_newest_point := points[-2]) not in scores:
        # if we don't have a score for the next newest point, i.e. a new point was added since last time,
        # we need to find one via reckoning, so we compute how well we can predict the newest point
        scores[next_newest_point] = reckon(points[-3], next_newest_point, points[-1])

    if len(points) <= buffer_size:
        # if we haven't exceeded the buffer size, we're done for now
        # NOTE that we do this after potentially finding the score, so we get the scores even when we're below the size threshold
        return points

    # now we need to find the point with the lowest score, not counting the first or last point since those don't have scores
    index_min = min(range(1, len(points) - 1), key=lambda i: scores[points[i]])

    # delete the element at the index we found and recompute scores for the affected points
    # NOTE pop removes AND returns the value, so we use it to remove the point's score as well
    del scores[points.pop(index_min)]
    if index_min != (len(points) - 1):
        # compute score for the new point at the chosen index if it's not the last
        scores[points[index_min]] = reckon(
            points[index_min - 1], points[index_min], points[index_min + 1]
        )
    if (index_min - 1) != 0:
        # compute score for the point at the preceding index if it's not the first
        scores[points[index_min - 1]] = reckon(
            points[index_min - 2], points[index_min - 1], points[index_min]
        )
    # the buffer should be the correct size again, and we've updated all the scores we need to update
    return points


def run_sr(route: Route, params: dict) -> Route:
    simplified_trajectory = []
    for vessel_log in route.trajectory:
        simplified_trajectory.append(vessel_log)
        simplified_trajectory = squish_reckoning(simplified_trajectory, params["buff_size"])

    return Route(simplified_trajectory)
