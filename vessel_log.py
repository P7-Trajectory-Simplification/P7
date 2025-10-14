from datetime import datetime
import numpy as np


class VesselLog:
    def __init__(self, lat: float, lon: float, ts: datetime):
        self.lat = lat
        self.lon = lon
        self.ts = ts

    def get_coords(self) -> tuple[float, float]:
        return np.radians(self.lat), np.radians(self.lon)