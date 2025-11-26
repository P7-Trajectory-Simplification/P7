from algorithms.great_circle_math import great_circle_distance
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog
from classes.priority_queue import PriorityQueue
import numpy as np

singleton = None


def run_squish_e(route: Route, params: dict) -> Route:
    global singleton
    if singleton is None:
        singleton = SquishE(params["low_comp"], params["max_sed"])
    squish_e = singleton

    for vessel_log in route.trajectory:
        squish_e.append_point(vessel_log)
        squish_e.simplify()
    return Route(squish_e.trajectory)


class SquishE(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["low_comp"], params["max_sed"])

    @property
    def name(self):
        return "SQUISH_E"

    def __init__(
        self, lower_compression_rate: float = 2.0, upper_bound_sed: float = 100.0
    ):
        super().__init__()
        self.lower_compression_rate = lower_compression_rate
        self.upper_bound_sed = upper_bound_sed
        self.buffer_size = 4
        self.buffer = PriorityQueue()  # Buffer is a priority queue
        self.max_neighbor: dict[int, float] = (
            {}
        )  # Maps point id to max sed of its neighbors

    def simplify(self):
        self.trajectory = self.squish_e(self.trajectory)

    def reduce(self):
        """
        Describes how the heap is reduced when the buffer size is full
        """
        point, priority = (
            self.buffer.remove_min()
        )  # Remove point with the lowest priority
        if (
            point.id in self.buffer.pred or point.id in self.buffer.succ
        ):  # Not the first or last point
            # Update max_neighbor for neighboring points
            self.max_neighbor[self.buffer.succ[point.id].id] = max(
                priority, self.max_neighbor[self.buffer.succ[point.id].id]
            )
            self.max_neighbor[self.buffer.pred[point.id].id] = max(
                priority, self.max_neighbor[self.buffer.pred[point.id].id]
            )

            # Update priority for neighboring points
            self.adjust_priority(self.buffer.pred[point.id])
            self.adjust_priority(self.buffer.succ[point.id])

        # Garbage Collection
        del self.max_neighbor[point.id]

    def adjust_priority(self, point: VesselLog):
        """
        Called when inserting and removing points and updates the priority (sed) of all the neighboring points
        """
        if (
            point.id in self.buffer.pred and point.id in self.buffer.succ
        ):  # Check if first or last point
            predecessor = self.buffer.pred[point.id]
            successor = self.buffer.succ[point.id]
            if predecessor is not None and successor is not None:
                if (
                    point.ts - predecessor.ts < successor.ts - point.ts
                ):  # Find nearest point in time to compute sed (This is not entirely correct squish-e)
                    # Closer to predecessor
                    priority = self.max_neighbor[point.id] + np.abs(
                        great_circle_distance(
                            point.get_coords(), predecessor.get_coords()
                        )
                    )
                else:
                    # Closer to successor
                    priority = self.max_neighbor[point.id] + np.abs(
                        great_circle_distance(
                            point.get_coords(), successor.get_coords()
                        )
                    )
                self.buffer.insert(
                    point, priority
                )  # Update priority in the priority queue

    def squish_e(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        """
        Implementation of the SQUISH-E algorithm, which is a trajectory simplification algorithm that works like SQUISH
        It implements an adaptable buffer and ensures all the points are at least of a certain importance
        """
        if (
            self.buffer.size() / self.lower_compression_rate >= self.buffer_size
        ):  # Increase buff_size based on lower bound compression rate
            self.buffer_size += 1

        new_point = trajectory[-1]  # Get the newest point
        self.buffer.insert(new_point)  # Insert point with priority = inf
        self.max_neighbor[new_point.id] = 0  # Initialize max_neighbor for the new point
        if self.buffer.size() > 2:  # After the first point
            predecessor = trajectory[-2]  # Get the predecessor point
            self.adjust_priority(predecessor)  # Update priority

        if self.buffer.size() == self.buffer_size + 1:  # Reduce buffer when full
            self.reduce()

        # After finishing looping through, keep reducing heap until all points satisfies upper bound on SED
        while self.buffer.min_priority() <= self.upper_bound_sed:
            self.reduce()

        return self.buffer.to_list()  # Return the points in the buffer as a list

    def __repr__(self):
        return (
            "SquishE Instance with "
            + f"lower_compression_rate={self.lower_compression_rate}, upper_bound_sed={self.upper_bound_sed}"
        )
