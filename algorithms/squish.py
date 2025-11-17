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
        squish.append_point(vessel_log)
        squish.simplify()
    return Route(squish.trajectory)


class Squish(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["buff_size"])

    @property
    def name(self):
        return "SQUISH"

    def __init__(self, buffer_size: int = 100):
        super().__init__()
        self.buffer_size = buffer_size
        self.buffer = PriorityQueue() # Buffer is a priority queue

    def simplify(self):
        self.trajectory = self.squish(self.trajectory)

    def update_sed(self, target: VesselLog):
        if target.id in self.buffer.pred and target.id in self.buffer.succ: # Not the first or last point
            predecessor = self.buffer.pred[target.id]
            successor = self.buffer.succ[target.id]

            if target.ts - predecessor.ts < successor.ts - target.ts:
                # Closer to predecessor
                sed = np.abs(great_circle_distance(predecessor.get_coords(), target.get_coords()))
            else:
                # Closer to successor
                sed = np.abs(great_circle_distance(successor.get_coords(), target.get_coords()))
            self.buffer.insert(target, sed) # Update the SED value in the priority queue

    def squish(self, trajectory: list[VesselLog]):
        new_point = trajectory[-1] # Get the newest point
        self.buffer.insert(new_point) # Insert it into the buffer with infinite SED

        if self.buffer.size() > 1:  # After the first point
            predecessor = trajectory[-2] # Get the predecessor point
            self.buffer.succ[predecessor.id] = new_point # Update successor mapping
            self.buffer.pred[new_point.id] = predecessor # Update predecessor mapping

            if self.buffer.size() > 2: # After the second point
                self.update_sed(predecessor) # Update SED of predecessor

        if self.buffer.size() == self.buffer_size + 1: # Buffer is full
            point, _ = self.buffer.remove_min() # Remove point with the smallest SED

            if point.id in self.buffer.pred or point.id in self.buffer.succ:
                self.update_sed(self.buffer.pred[point.id]) # Update SED of predecessor
                self.update_sed(self.buffer.succ[point.id]) # Update SED of successor

        return self.buffer.to_list() # Return the points in the buffer as a list
