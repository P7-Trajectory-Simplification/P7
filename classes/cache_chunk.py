from classes.vessel_log import VesselLog


class CacheChunk:
    def __init__(self, vessel_logs: list[VesselLog]):
        self.vessel_logs = vessel_logs

    def first_log(self) -> VesselLog:
        return self.vessel_logs[0]

    def last_log(self) -> VesselLog:
        return self.vessel_logs[-1]

    def from_date(self):
        return self.first_log().ts

    def to_date(self):
        return self.last_log().ts