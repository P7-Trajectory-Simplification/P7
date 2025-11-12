from algorithms.great_circle_math import point_to_great_circle
from classes.route import Route
from classes.vessel_log import VesselLog
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

    dp.trajectory = route.trajectory
    dp.simplify()

    return Route(dp.trajectory)


class DouglasPeucker(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["epsilon"])

    def __init__(self, epsilon: float):
        super().__init__()
        self.epsilon = epsilon

    def simplify(self):
        self.trajectory = self.douglas_peucker(self.trajectory)

    def douglas_peucker(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        '''
        Simplifies a given set of points using the Douglas-Peucker algorithm.

        Parameters
        ---------
        points (list of tuples): List of (lat, lon) coordinates representing the points.
        epsilon (float): The maximum distance threshold for simplification.

        Returns
        ---------
        list of tuples: Simplified list of points.
        '''
        dmax = 0
        index = 0
        end = len(trajectory) - 1
        for i in range(1, end):
            # Calculate the perpendicular distance from point to line segment
            d = np.abs(
                point_to_great_circle(
                    trajectory[0].get_coords(),
                    trajectory[end].get_coords(),
                    trajectory[i].get_coords(),
                )
            )
            if d > dmax:
                index = i
                dmax = d

        if dmax > self.epsilon:
            rec_results1 = self.douglas_peucker(trajectory[: index + 1])
            rec_results2 = self.douglas_peucker(trajectory[index:])

            return rec_results1[:-1] + rec_results2
        return [trajectory[0], trajectory[end]]
