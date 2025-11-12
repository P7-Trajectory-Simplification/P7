from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog

singleton = None


def run_uniform_sampling(route: Route, params: dict) -> Route:
    global singleton
    if singleton is None:
        singleton = UniformSampling(params["sampling_rate"])
    uniform_sampling = singleton

    uniform_sampling.trajectory = route.trajectory
    uniform_sampling.simplify()

    return Route(uniform_sampling.trajectory)


class UniformSampling(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["sampling_rate"])

    def __init__(self, sampling_rate: int = 10):
        super().__init__()
        self.sampling_rate = sampling_rate
        if self.sampling_rate <= 0:
            raise ValueError("Frequency must be a positive number.")

    def simplify(self):
        self.trajectory = self.uniform_sampling(self.trajectory)

    def uniform_sampling(self, points: list[VesselLog]) -> list[VesselLog]:
        '''
        Simplifies a given set of points using uniform sampling.

        Parameters
        ---------
        points (list of VesselLog): List of VesselLog objects representing the points.

        Returns
        ---------
        list of VesselLog: Simplified list of points.
        '''
        sampled_points = []
        for i in range(0, len(points), self.sampling_rate):
            sampled_points.append(points[i])

        # Ensure the last point is included
        if points[-1] not in sampled_points:
            sampled_points.append(points[-1])

        return sampled_points
