from datetime import datetime

from classes.squish_point import SquishPoint
from classes.vessel_log import VesselLog


class Route:
    def __init__(self, trajectory: list[VesselLog] = None, squish_buff: list[SquishPoint] = None, squish_e_buff: list[VesselLog] = None):
        self.trajectory = trajectory or []
        self.squish_buff = squish_buff or []
        self.squish_e_buff = squish_e_buff or []

    def to_list(self) -> list[tuple[float, float, datetime]]:
        return [(log.lat, log.lon, log.ts) for log in self.trajectory]

    def extract_squish_buffer(self) -> list[VesselLog]:
        simplified_trajectory = []
        for squish_point in self.squish_buff:
            simplified_trajectory.append(squish_point.vessel_log)
        return simplified_trajectory