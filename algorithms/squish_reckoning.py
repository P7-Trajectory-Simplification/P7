from algorithms.dead_reckoning import reckon
from classes.priority_queue import PriorityQueue
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog

"""
# memoization of VesselLogs' scores. Remember to delete logs that aren't in the buffer!
scores = {}
"""


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
        singleton = SquishReckoning(params["buff_size"])
    sr = singleton
    for vessel_log in route.trajectory:
        sr.append_point(vessel_log)
        sr.simplify()
    return Route(sr.trajectory)


class SquishReckoning(Simplifier):
    @classmethod
    def from_params(cls, params, math):
        return cls(
            params["buff_size"],
            math["point_to_point_distance"],
            math["get_final_bearing"],
            math["predict_sphere_movement"],
        )

    @property
    def name(self):
        return "SQUISH_RECKONING"

    def __init__(
        self,
        buffer_size: int = 100,
        point_to_point_distance=None,
        get_final_bearing=None,
        predict_sphere_movement=None,
    ):
        super().__init__(
            point_to_point_distance=point_to_point_distance,
            get_final_bearing=get_final_bearing,
            predict_sphere_movement=predict_sphere_movement,
        )
        self.buffer_size = buffer_size
        self.buffer = PriorityQueue()
        self.mode = "online"

    def simplify(self):
        self.trajectory = self.squish_reckoning(self.trajectory)

    def squish_reckoning(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        new_point = trajectory[-1]  # Get the newest point
        self.buffer.insert(new_point)  # Insert it into the buffer with infinite score

        if self.buffer.size() > 2:  # After the second point
            predecessor = trajectory[-2]  # Get the predecessor point
            score = reckon(
                self.buffer.pred[predecessor.id],
                predecessor,
                self.buffer.succ[predecessor.id],
                self.point_to_point_distance,
                self.get_final_bearing,
                self.predict_sphere_movement,
            )  # Calculate the score
            self.buffer.insert(
                predecessor, score
            )  # Update the score of the predecessor in the buffer

        if (
            self.buffer.size() == self.buffer_size + 1
        ):  # Buffer full, need to remove one point
            point, _ = self.buffer.remove_min()  # Remove point with the lowest score

            if point.id in self.buffer.pred:  # Not the first point
                predecessor = self.buffer.pred[point.id]  # Get predecessor
                self.buffer.insert(
                    predecessor,
                    reckon(
                        self.buffer.pred[predecessor.id],
                        predecessor,
                        self.buffer.succ[predecessor.id],
                        self.point_to_point_distance,
                        self.get_final_bearing,
                        self.predict_sphere_movement,
                    ),
                )  # Recalculate and update score of predecessor

            if point.id in self.buffer.succ:  # Not the last point
                successor = self.buffer.succ[point.id]  # Get successor
                self.buffer.insert(
                    successor,
                    reckon(
                        self.buffer.pred[successor.id],
                        successor,
                        self.buffer.succ[successor.id],
                        self.point_to_point_distance,
                        self.get_final_bearing,
                        self.predict_sphere_movement,
                    ),
                )  # Recalculate and update score of successor
        return self.buffer.to_list()  # Return the points in the buffer as a list
