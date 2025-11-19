from classes.vessel_log import VesselLog


class CacheChunk:
    def __init__(self, vessel_logs: list[VesselLog]):
        self.vessel_logs = vessel_logs # A list of VesselLog objects

    def first_log(self) -> VesselLog:
        # Return the first VesselLog in the list
        return self.vessel_logs[0]

    def last_log(self) -> VesselLog:
        # Return the last VesselLog in the list
        return self.vessel_logs[-1]

    def from_date(self):
        # Return the timestamp of the first VesselLog
        return self.first_log().ts

    def to_date(self):
        # Return the timestamp of the last VesselLog
        return self.last_log().ts