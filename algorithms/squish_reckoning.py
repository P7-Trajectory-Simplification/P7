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
        sr.trajectory.append(vessel_log)
        sr.simplify()
    return Route(sr.trajectory)


class SquishReckoning(Simplifier):
    def __init__(self, buffer_size: int = 100):
        super().__init__()
        self.buffer_size = buffer_size
        # memoization of VesselLogs' scores. Remember to delete logs that aren't in the buffer!
        self.scores = {}
        self.heap = PriorityQueue()

    def simplify(self):
        self.trajectory = self.squish_reckoning(self.trajectory)

    def squish_reckoning(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        if len(trajectory) < 3:
            # nothing to do, and buffer size shouldn't be considered since we always want the first and last point
            return trajectory

        if (next_newest_point := trajectory[-2]) not in self.scores:
            # if we don't have a score for the next newest point, i.e. a new point was added since last time,
            # we need to find one via reckoning, so we compute how well we can predict the newest point
            self.scores[next_newest_point] = reckon(
                trajectory[-3], next_newest_point, trajectory[-1]
            )

        if len(trajectory) <= self.buffer_size:
            # if we haven't exceeded the buffer size, we're done for now
            # NOTE that we do this after potentially finding the score, so we get the scores even when we're below the size threshold
            return trajectory

        # now we need to find the point with the lowest score, not counting the first or last point since those don't have scores
        index_min = min(range(1, len(trajectory) - 1), key=lambda i: self.scores[trajectory[i]])

        # delete the element at the index we found and recompute scores for the affected points
        # NOTE pop removes AND returns the value, so we use it to remove the point's score as well
        del self.scores[trajectory.pop(index_min)]
        if index_min != (len(trajectory) - 1):
            # compute score for the new point at the chosen index if it's not the last
            self.scores[trajectory[index_min]] = reckon(
                trajectory[index_min - 1], trajectory[index_min], trajectory[index_min + 1]
            )
        if (index_min - 1) != 0:
            # compute score for the point at the preceding index if it's not the first
            self.scores[trajectory[index_min - 1]] = reckon(
                trajectory[index_min - 2], trajectory[index_min - 1], trajectory[index_min]
            )
        # the buffer should be the correct size again, and we've updated all the scores we need to update
        return trajectory
