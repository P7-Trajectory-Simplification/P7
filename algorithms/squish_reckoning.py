from algorithms.dead_reckoning import reckon
from classes.priority_queue import PriorityQueue
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog

'''
# memoization of VesselLogs' scores. Remember to delete logs that aren't in the buffer!
scores = {}
'''


# singleton just for the proof of concept
singleton = None


def run_sr(route: Route, params: dict) -> Route:
    # old run_sr code:
    # simplified_trajectory = []
    # for vessel_log in route.trajectory:
    #    simplified_trajectory.append(vessel_log)
    #    simplified_trajectory = squish_reckoning(
    #        simplified_trajectory, params['buff_size']
    #    )
    #
    # return Route(simplified_trajectory)

    # proof of concept to show how the class works
    global singleton
    if singleton is None:
        singleton = SquishReckoning(params['buff_size'])
    sr = singleton
    for vessel_log in route.trajectory:
        sr.append_point(vessel_log)
        sr.simplify()
    return Route(sr.trajectory)


class SquishReckoning(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["buff_size"])

    @property
    def name(self):
        return "SQUISH_RECKONING"

    def __init__(self, buffer_size: int = 100):
        super().__init__()
        self.buffer_size = buffer_size
        self.buffer = PriorityQueue()

    def simplify(self):
        self.trajectory = self.squish_reckoning(self.trajectory)

    def squish_reckoning(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        new_point = trajectory[-1]
        self.buffer.insert(new_point, float('inf'))

        if self.buffer.size() > 1:  # After the first point
            predecessor = trajectory[-2]
            self.buffer.succ[predecessor.id] = new_point
            self.buffer.pred[new_point.id] = predecessor


        if self.buffer.size() > 2: # After the second point
            predecessor = trajectory[-2]
            score = reckon(
                self.buffer.pred[predecessor.id],
                predecessor,
                self.buffer.succ[predecessor.id]
            )
            self.buffer.insert(predecessor, score)

        if self.buffer.size() == self.buffer_size + 1:
            point, _ = self.buffer.remove_min()

            if point.id in self.buffer.pred:
                predecessor = self.buffer.pred[point.id]
                self.buffer.insert(
                    predecessor,
                    reckon(
                        self.buffer.pred[predecessor.id],
                        predecessor,
                        self.buffer.succ[predecessor.id]
                    )
                )

            if point.id in self.buffer.succ:
                successor = self.buffer.succ[point.id]
                self.buffer.insert(
                    successor,
                    reckon(
                        self.buffer.pred[successor.id],
                        successor,
                        self.buffer.succ[successor.id]
                    )
                )
        return self.buffer.to_list()
