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

    def __init__(
        self, lower_compression_rate: float = 2.0, upper_bound_sed: float = 100.0
    ):
        super().__init__()
        self.lower_compression_rate = lower_compression_rate
        self.upper_bound_sed = upper_bound_sed
        self.buffer_size = 4
        self.buffer: list[VesselLog] = []
        self.heap = PriorityQueue()
        self.predecessor = {}
        self.successor = {}
        self.max_neighbor = {}

    def simplify(self):
        self.trajectory = self.squish_e(self.trajectory)

    def reduce(self):
        """
        Describes how the heap is reduced when the buffer size is full
        """

        id, _, priority = self.heap.remove_min()

        self.max_neighbor[self.successor[id]] = max(
            priority, self.max_neighbor[self.successor[id]]
        )
        self.max_neighbor[self.predecessor[id]] = max(
            priority, self.max_neighbor[self.predecessor[id]]
        )

        self.successor[self.predecessor[id]] = self.successor[
            id
        ]  # register succ[Pj] as the closest successor of pred[Pj]
        self.predecessor[self.successor[id]] = self.predecessor[
            id
        ]  # register pred[Pj] as the closest predecessor of succ[Pj]

        # Adjust neighboring points
        self.adjust_priority(self.predecessor[id])
        self.adjust_priority(self.successor[id])

        # Garbage Collection
        del self.predecessor[id]
        del self.successor[id]
        del self.max_neighbor[id]

    def adjust_priority(self, point_id: int):
        """
        Called when inserting and removing points and updates the priority (sed) of all the neighboring points

        Parameters
        ---------
        point_id: int
            The ID of the point that has to be updated
        """
        point = self.trajectory[point_id]
        if (
            point_id in self.predecessor and point_id in self.successor
        ):  # Check if first or last point
            before = self.trajectory[self.predecessor[point_id]]
            after = self.trajectory[self.successor[point_id]]
            if (
                point.ts - before.ts < after.ts - point.ts
            ):  # Find nearest point in time to compute sed (This is not entirely correct squish-e)
                priority = self.max_neighbor[point_id] + np.abs(
                    great_circle_distance(point.get_coords(), before.get_coords())
                )
            else:
                priority = self.max_neighbor[point_id] + np.abs(
                    great_circle_distance(point.get_coords(), after.get_coords())
                )
            self.heap.insert(point_id, point, priority)

    def squish_e(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        """
        Implementation of the SQUISH-E algorithm, which is a trajectory simplification algorithm that works like SQUISH
        It implements an adaptable buffer and ensures all the points are at least of a certain importance

        Parameters
        --------------
        trajectory: list[VesselLog]
            A list of all the raw data points that needs to be compressed
        """

        for i in range(0, len(trajectory)):

            if (
                i / self.lower_compression_rate >= self.buffer_size
            ):  # increase buff_size based on lower bound compression rate
                self.buffer_size += 1

            self.heap.insert(
                i, trajectory[i], float('inf')
            )  # Insert point with priority = inf
            self.max_neighbor[i] = 0

            if i > 0:  # After the first point
                self.successor[i - 1] = i
                self.predecessor[i] = i - 1
                self.adjust_priority(i - 1)  # update priority

            if len(self.heap.heap) == self.buffer_size:  # Reduce buffer when full
                self.reduce()

        # After finishing looping through, keep reducing heap until all points satisfies upper bound on SED
        while self.heap.min_priority() <= self.upper_bound_sed:
            self.reduce()

        # The first point is the one with 0 predecessors
        start = next(
            (pid for pid in self.predecessor if self.predecessor[pid] is None), 0
        )
        curr = start
        while curr is not None:  # Add each point in order
            self.buffer.append(trajectory[curr])
            curr = self.successor.get(curr)

        return self.buffer
