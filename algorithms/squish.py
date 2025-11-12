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
    def __init__(self, buffer_size: int = 100):
        super().__init__()
        self.buffer_size = buffer_size
        self.buffer: list[VesselLog] = []
        self.heap = PriorityQueue()

    def simplify(self):
        self.trajectory = self.squish(self.trajectory)

    def update_sed(self, index: int):
        if index in self.heap.predecessor and index in self.heap.successor:
            a = self.trajectory[self.heap.predecessor[index]]
            b = self.trajectory[self.heap.successor[index]]
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

            if self.heap.size() >= 3:
                self.update_sed(i-1)

            if self.heap.size() == self.buffer_size + 1:
                index, _, _ = self.heap.remove_min()

                if index in self.heap.predecessor and index in self.heap.successor:
                    self.update_sed(self.heap.predecessor[index])
                    self.update_sed(self.heap.successor[index])

        self.buffer = self.heap.get_points(trajectory)
        return self.buffer
