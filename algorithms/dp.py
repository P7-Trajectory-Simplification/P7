import numpy as np
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog

singleton = None


def run_dp(route: Route, params: dict) -> Route:
    global singleton
    if singleton is None:
        singleton = DouglasPeucker(params["epsilon"])
    dp = singleton

    for vessel_log in route.trajectory:
        dp.append_point(vessel_log)
        dp.simplify()

    return Route(dp.trajectory)


class DouglasPeucker(Simplifier):
    @classmethod
    def from_params(cls, params, math):
        return cls(params["epsilon"], math["point_to_line_distance"])

    @property
    def name(self):
        return "DP"

    def __init__(self, epsilon: float, point_to_line_distance=None):
        super().__init__(point_to_line_distance=point_to_line_distance)
        self.epsilon = epsilon
        self.original_trajectory = []
        self.mode = "batch"

    def append_point(self, point):
        self.original_trajectory.append(point)

    def simplify(self):
        self.trajectory = self.douglas_peucker(self.original_trajectory)

    def douglas_peucker(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        """
        Simplifies a given set of points using the Douglas-Peucker algorithm.
        """
        dmax = 0  # Maximum distance
        index = 0  # Index of the point with maximum distance
        end = len(trajectory) - 1  # Index of the last point
        for i in range(1, end):
            # Calculate the perpendicular distance from point to line segment
            d = np.abs(
                self.point_to_line_distance(
                    trajectory[0].get_coords(),
                    trajectory[end].get_coords(),
                    trajectory[i].get_coords(),
                )
            )
            if d > dmax:  # Update maximum distance and index
                index = i
                dmax = d

        if (
            dmax > self.epsilon
        ):  # If maximum distance is greater than epsilon, recursively simplify
            rec_results1 = self.douglas_peucker(trajectory[: index + 1])
            rec_results2 = self.douglas_peucker(trajectory[index:])

            return (
                rec_results1[:-1] + rec_results2
            )  # Combine results excluding the last point of the first half to avoid duplication
        return [trajectory[0], trajectory[end]]  # Return start and end points

    def __repr__(self):
        return "DouglasPeucker Instance with " + f"epsilon={self.epsilon}"
