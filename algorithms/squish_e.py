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
        squish_e.trajectory.append(vessel_log)
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
        self.buffer = PriorityQueue()
        self.max_neighbor: dict[int, float] = {}

    def simplify(self):
        self.trajectory = self.squish_e(self.trajectory)

    def reduce(self):
        """
        Describes how the heap is reduced when the buffer size is full
        """
        point, priority = self.buffer.remove_min()
        self.trajectory.remove(point)
        if point.id in self.buffer.pred or point.id in self.buffer.succ:
            self.max_neighbor[self.buffer.succ[point.id].id] = max(priority, self.max_neighbor[self.buffer.succ[point.id].id])
            self.max_neighbor[self.buffer.pred[point.id].id] = max(priority, self.max_neighbor[self.buffer.pred[point.id].id])

            # Adjust neighboring points
            self.adjust_priority(self.buffer.pred[point.id])
            self.adjust_priority(self.buffer.succ[point.id])

        # Garbage Collection
        del self.max_neighbor[point.id]

    def adjust_priority(self, point: VesselLog):
        """
        Called when inserting and removing points and updates the priority (sed) of all the neighboring points
        """
        if point.id in self.buffer.pred and point.id in self.buffer.succ:  # Check if first or last point
            predecessor = self.buffer.pred[point.id]
            successor = self.buffer.succ[point.id]
            if point.ts - predecessor.ts < successor.ts - point.ts:  # Find nearest point in time to compute sed (This is not entirely correct squish-e)
                priority = self.max_neighbor[point.id] + np.abs(
                    great_circle_distance(point.get_coords(), predecessor.get_coords()))
            else:
                priority = self.max_neighbor[point.id] + np.abs(
                    great_circle_distance(point.get_coords(), successor.get_coords()))
            self.buffer.insert(point, priority)

    def squish_e(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        """
        Implementation of the SQUISH-E algorithm, which is a trajectory simplification algorithm that works like SQUISH
        It implements an adaptable buffer and ensures all the points are at least of a certain importance

        Parameters
        --------------
        trajectory: list[VesselLog]
            A list of all the raw data points that needs to be compressed
        """
        if self.buffer.size() / self.lower_compression_rate >= self.buffer_size:  # increase buff_size based on lower bound compression rate
            self.buffer_size += 1

        new_point = trajectory[-1]
        self.buffer.insert(new_point, float('inf'))  # Insert point with priority = inf
        self.max_neighbor[new_point.id] = 0
        if self.buffer.size() > 1:  # After the first point
            predecessor = trajectory[-2]
            self.buffer.succ[predecessor.id] = new_point
            self.buffer.pred[new_point.id] = predecessor
            self.adjust_priority(predecessor)  # update priority

        if self.buffer.size() == self.buffer_size + 1:  # Reduce buffer when full
            self.reduce()

        # After finishing looping through, keep reducing heap until all points satisfies upper bound on SED
        while self.buffer.min_priority() <= self.upper_bound_sed:
            self.reduce()

        return trajectory
