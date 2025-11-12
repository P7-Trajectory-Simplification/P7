from algorithms.great_circle_math import great_circle_distance
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog
from classes.priority_queue import PriorityQueue
import numpy as np

singleton = None


def run_squish(route: Route, params: dict) -> Route:
    global singleton
    if singleton is None:
        singleton = Squish(params["buff_size"])
    squish = singleton

    for vessel_log in route.trajectory:
        squish.trajectory.append(vessel_log)
        squish.simplify()
    return Route(squish.trajectory)


class Squish(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["buff_size"])

    def __init__(self, buffer_size: int = 100):
        super().__init__()
        self.buffer_size = buffer_size
        self.buffer: list[VesselLog] = []
        self.heap = PriorityQueue()
        self.successor = {}
        self.predecessor = {}

    def simplify(self):
        self.trajectory = self.squish(self.trajectory)

    def update_sed(self, index: int):
        if index in self.predecessor and index in self.successor:
            a = self.trajectory[self.predecessor[index]]
            b = self.trajectory[self.successor[index]]
            target = self.trajectory[index]

            if target.ts - a.ts < b.ts - target.ts:
                # Closer to a
                sed = np.abs(great_circle_distance(a.get_coords(), target.get_coords()))
            else:
                # Closer to b
                sed = np.abs(great_circle_distance(b.get_coords(), target.get_coords()))

            self.heap.insert(index, target, sed)

    def squish(self, trajectory: list[VesselLog]):
        for i in range(len(trajectory)):
            self.heap.insert(i, trajectory[i], float('inf'))

            if i > 0:  # After the first point
                self.successor[i - 1] = i
                self.predecessor[i] = i - 1

            if self.heap.size() >= 3:
                self.update_sed(i - 1)

            if self.heap.size() == self.buffer_size + 1:
                index, _, _ = self.heap.remove_min()

                self.successor[self.predecessor[index]] = self.successor[index]
                self.predecessor[self.successor[index]] = self.predecessor[index]
                del self.predecessor[index]
                del self.successor[index]

                if index in self.predecessor and index in self.successor:
                    self.update_sed(self.predecessor[index])
                    self.update_sed(self.successor[index])

        # The first point is the one with 0 predecessors
        start = next(
            (pid for pid in self.predecessor if self.predecessor[pid] is None), 0
        )
        curr = start
        while curr is not None:  # Add each point in order
            self.buffer.append(trajectory[curr])
            curr = self.successor.get(curr)

        return self.buffer
