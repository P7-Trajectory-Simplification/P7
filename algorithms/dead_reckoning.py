import numpy as np
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog

singleton = None


def run_dr(route: Route, params: dict) -> Route:
    global singleton
    if singleton is None:
        singleton = DeadReckoning(params["tolerance"])
    dr = singleton

    for vessel_log in route.trajectory:
        dr.append_point(vessel_log)
        dr.simplify()

    return Route(dr.trajectory)


class DeadReckoning(Simplifier):
    @classmethod
    def from_params(cls, params, math):
        return cls(
            params["tolerance"],
            math["point_to_point_distance"],
            math["get_final_bearing"],
            math["predict_sphere_movement"]
        )

    @property
    def name(self):
        return "DR"

    def __init__(
        self,
        tolerance: int = 100,
        point_to_point_distance=None,
        get_final_bearing=None,
        predict_sphere_movement=None
    ):
        super().__init__(
            point_to_point_distance=point_to_point_distance,
            get_final_bearing=get_final_bearing,
            predict_sphere_movement=predict_sphere_movement
        )
        self.tolerance = tolerance
        self.prediction_startpoint = None
        self.prediction_endpoint = None

    def simplify(self):
        self.trajectory = self.dead_reckoning(self.trajectory)

    def dead_reckoning(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        if len(trajectory) < 2:  # Need at least two points to make a prediction
            return trajectory
        elif len(trajectory) == 2:  # Initialize prediction points
            self.prediction_startpoint = trajectory[-2]
            self.prediction_endpoint = trajectory[-1]
            return trajectory

        reckon(
            self.prediction_startpoint,
            self.prediction_endpoint,
            trajectory[-1],
            self.point_to_point_distance,
            self.get_final_bearing,
            self.predict_sphere_movement
        )

        next_newest_point = trajectory[-2]
        newest_point = trajectory[-1]

        error = reckon(
            self.prediction_startpoint,
            self.prediction_endpoint,
            newest_point,
            self.point_to_point_distance,
            self.get_final_bearing,
            self.predict_sphere_movement
        )

        if np.abs(error) > self.tolerance:
            # if the predicted point is further than we tolerate, reset prediction points
            self.prediction_startpoint = next_newest_point
            self.prediction_endpoint = newest_point
        else:
            # if the predicted point is close enough, we don't need the next newest point anymore and can safely exclude it
            del trajectory[-2]
        return trajectory

    def __repr__(self):
        return "DeadReckoning Instance with " + f"tolerance={self.tolerance}"


# Helper function for squish reckoning
def reckon(
        point_a: VesselLog,
        point_b: VesselLog,
        point_c: VesselLog,
        great_circle_distance,
        get_final_bearing,
        predict_sphere_movement
) -> float:
    '''Given three points with latitude, longitude, and timestamp, return the distance between point c and point c as predicted by point a and b via dead reckoning

    Parameters
    ----------
        :param point_a: The log representing the first point.
        :param point_b: The log representing the second point. It is this point we attribute the returned value distance to.
        :param point_c: The log representing the point to predict.
        :param predict_sphere_movement:
        :param get_final_bearing:
        :param great_circle_distance:
    '''
    latlon_a = point_a.get_coords()
    latlon_b = point_b.get_coords()

    # find distance from A to B
    distance = great_circle_distance(latlon_a, latlon_b)
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
        latlon_b, prediction_distance, prediction_bearing
    )
    # return distance from predicted C to actual C
    return great_circle_distance(c_predicted, point_c.get_coords())
