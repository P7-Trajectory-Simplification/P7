from datetime import datetime
from great_circle_math import (
    great_circle_distance,
    predict_sphere_movement,
    get_final_bearing,
    EARTH_RADIUS_METERS,
)
import os, sys

# need to import os and sys to get the placement of this file, so we can get its root folder and grab VesselLog from there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vessel_log import VesselLog

prediction_startpoint = None
prediction_endpoint = None


def dead_reckoning(
    points: list[VesselLog],
    tolerance: int = 100,
    distance_formula=great_circle_distance,
    prediction_formula=predict_sphere_movement,
    bearing_formula=get_final_bearing,
):
    global prediction_startpoint
    global prediction_endpoint

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
    if (
        great_circle_distance(
            latlon_predicted, newest_point.get_coords(), radius=EARTH_RADIUS_METERS
        )
        > tolerance
    ):
        # if the predicted point is further than we tolerate, reset prediction points
        prediction_startpoint = next_newest_point
        prediction_endpoint = newest_point
    else:
        # if the predicted point is close enough, we don't need the next newest point anymore and can safely exclude it
        del points[-2]
    return points


if __name__ == "__main__":
    test_points = [
        VesselLog(57.020442, 10.016914, datetime(2020, 1, 1)),
        VesselLog(57.021980, 10.017974, datetime(2020, 1, 2)),
        VesselLog(57.023364, 10.018927, datetime(2020, 1, 3)),
        VesselLog(57.024037, 10.020870, datetime(2020, 1, 4)),
        VesselLog(57.023422, 10.023484, datetime(2020, 1, 5)),
    ]
    print(test_points)
    simplified_points = []
    for point in test_points:
        simplified_points.append(point)
        simplified_points = dead_reckoning(simplified_points, tolerance=2000)
    print(simplified_points)
