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

    @property
    def name(self):
        return "SQUISH"

    def __init__(self, buffer_size: int = 100):
        super().__init__()
        self.buffer_size = buffer_size
        self.buffer = PriorityQueue()

    def simplify(self):
        self.trajectory = self.squish(self.trajectory)

    def update_sed(self, target: VesselLog):
        if target.id in self.buffer.pred and target.id in self.buffer.succ:
            predecessor = self.buffer.pred[target.id]
            successor = self.buffer.succ[target.id]

            if target.ts - predecessor.ts < successor.ts - target.ts:
                # Closer to a
                sed = np.abs(great_circle_distance(predecessor.get_coords(), target.get_coords()))
            else:
                # Closer to b
                sed = np.abs(great_circle_distance(successor.get_coords(), target.get_coords()))
            self.buffer.insert(target, sed)

    def squish(self, trajectory: list[VesselLog]):
        new_point = trajectory[-1]
        self.buffer.insert(new_point)

        if self.buffer.size() > 1:  # After the first point
            predecessor = trajectory[-2]
            self.buffer.succ[predecessor.id] = new_point
            self.buffer.pred[new_point.id] = predecessor

            if self.buffer.size() >= 3:
                self.update_sed(predecessor)

        if self.buffer.size() == self.buffer_size + 1:
            point, _ = self.buffer.remove_min()

            if point.id in self.buffer.pred or point.id in self.buffer.succ:
                self.update_sed(self.buffer.pred[point.id])
                self.update_sed(self.buffer.succ[point.id])

        return self.buffer.to_list()
