from algorithms.great_circle_math import great_circle_distance
from classes.route import Route
from classes.simplifier import Simplifier
from classes.squish_point import SquishPoint
from classes.vessel_log import VesselLog
import numpy as np

singleton = None

#TODO: Change to new implementation of squish in main

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
    def __init__(self, buff_size: int = 100):
        super().__init__()
        self.buff_size = buff_size
        self.buffer: list[SquishPoint] = []

    def simplify(self):
        self.trajectory = self.squish(self.trajectory)

    def find_min_sed(self) -> int:
        if len(self.buffer) <= 2:
            return 0
        return min(range(1, len(self.buffer) - 1), key=lambda i: self.buffer[i].sed)

    def update_sed(self, index: int):
        a = self.buffer[index - 1].vessel_log
        b = self.buffer[index + 1].vessel_log
        target = self.buffer[index].vessel_log

        if target.ts - a.ts < b.ts - target.ts:
            # Closer to a
            self.buffer[index].sed = np.abs(great_circle_distance(a.get_coords(), target.get_coords()))
        else:
            # Closer to b
            self.buffer[index].sed = np.abs(great_circle_distance(b.get_coords(), target.get_coords()))

    def squish(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        for i in range(0, len(trajectory)):
            self.buffer.append(SquishPoint(trajectory[i], float('inf')))
            buff_length = len(self.buffer)
            if buff_length >= 3:
                self.update_sed(buff_length - 2)
            if buff_length == self.buff_size:
                index = self.find_min_sed()
                del self.buffer[index]
                buff_length = len(self.buffer)
                if 1 < index:
                    self.update_sed(index - 1)
                if index < buff_length - 1:
                    self.update_sed(index)
        return self.buffer
