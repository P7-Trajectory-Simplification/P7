from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog

singleton = None


def run_uniform_sampling(route: Route, params: dict) -> Route:
    global singleton
    if singleton is None:
        singleton = UniformSampling(params["sampling_rate"])
    uniform_sampling = singleton

    for vessel_log in route.trajectory:
        uniform_sampling.append_point(vessel_log)
        uniform_sampling.simplify()

    return Route(uniform_sampling.trajectory)


class UniformSampling(Simplifier):
    @classmethod
    def from_params(cls, params):
        return cls(params["sampling_rate"])

    @property
    def name(self):
        return "UNIFORM_SAMPLING"

    def __init__(self, sampling_rate: int = 10):
        super().__init__()
        self.sampling_rate = sampling_rate
        self.counter = (0,)
        mode = "online"
        if (
            self.sampling_rate < 3
        ):  # To keep the first, last and at least one middle point to remove
            raise ValueError("Frequency must be a positive number and bigger than 3.")

    def append_point(self, point):
        self.trajectory.append(point)
        self.counter += 1

    def simplify(self):
        self.trajectory = self.uniform_sampling(self.trajectory)

    def uniform_sampling(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        """
        Simplifies a given set of points using uniform sampling.

        Parameters
        ---------
        points (list of VesselLog): List of VesselLog objects representing the points.

        Returns
        ---------
        list of VesselLog: Simplified list of points.
        """
        if self.counter == self.sampling_rate:  # If counter reaches sampling rate
            self.counter = 0  # Reset counter
        elif len(self.trajectory) > 2:  # If not, and there are more than 2 points
            trajectory.pop(-2)  # Remove the second last point
        return trajectory  # Return the (maybe) simplified trajectory

    def __repr__(self):
        return "UniformSampling Instance with " + f"sampling_rate={self.sampling_rate}"
