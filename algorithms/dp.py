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

    def compression_bounded_douglas_peucker(
        self, trajectory: list[VesselLog], target_ratio=0.2
    ) -> list[VesselLog]:
        # point_indexes holds the indexes of the points we want to for the simplified trajectory, starting with the first and last indexes
        point_indexes = [0, len(trajectory) - 1]
        # NOTE An optimization is possible! We save dmax for each anchor segment and only recompute it when the segment is split (or newly created)
        dmaxes = {}  # maps segments to the maximum d from that segment
        # we'll try to index dmaxes with our segment and only compute d if there's no value for that segment
        # When we split a segment, we'll delete that segment's entry
        while len(point_indexes) / len(trajectory) < target_ratio:
            # keep adding points to the simplified trajectory until we're above the target compression ratio
            # this is done by finding the point furthest from its anchor segment and saving that distance (dmax),
            # its index (dmax_index), and where to place it in the simplified trajectory (segment_index)
            dmax = -1
            dmax_index = None
            segment_index = None
            for i in range(len(point_indexes) - 1):
                # we express our anchor segments as pairs of indexes so we go from the first point to the second-to-last point
                segment_start = point_indexes[i]
                segment_end = point_indexes[i + 1]
                # d is the greatest distance of any relevant point from the current segment
                # If the segment has no points other than the start and end, d defaults to -1 and d_index to None
                d, d_index = dmaxes.get(
                    segment_start,
                    max(
                        (  # NOTE the use of a generator expression instead of a list comprehension, to save memory
                            (
                                self.point_to_line_distance(
                                    trajectory[segment_start].get_coords(),
                                    trajectory[segment_end].get_coords(),
                                    trajectory[j].get_coords(),
                                ),
                                j,
                            )
                            for j in range(segment_start + 1, segment_end)
                        ),
                        default=(-1, None),
                    ),
                )
                dmaxes[segment_start] = (d, d_index)
                if d > dmax:
                    dmax = d
                    dmax_index = d_index
                    segment_index = i
            # once we're done iterating over our points, we insert the index for the point that resulted in dmax
            # directly between the start and endpoint of its anchor segment
            point_indexes.insert(segment_index + 1, dmax_index)
            del dmaxes[segment_index]
        # we're done finding our points, now we just build and return the simplified trajectory
        return [trajectory[i] for i in point_indexes]

    def __repr__(self):
        return "DouglasPeucker Instance with " + f"epsilon={self.epsilon}"
