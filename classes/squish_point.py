from classes.vessel_log import VesselLog

class SquishPoint:
    def __init__(self, vessel_log: VesselLog, sed: float):
        self.vessel_log = vessel_log
        self.sed = sed