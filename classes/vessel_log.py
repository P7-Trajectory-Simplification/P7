from datetime import datetime
import numpy as np


class VesselLog:
    def __init__(self, lat: float, lon: float, ts: datetime, imo: int):
        self.lat = lat
        self.lon = lon
        self.ts = ts
        self.imo = imo

    def get_coords(self) -> tuple[float, float]:
        return np.radians(self.lat), np.radians(self.lon)

    def strip_imo(self):
        """Delete the IMO from the VesselLog and free up the memory space."""
        del self.imo

    def __repr__(self):
        return f"({self.lat}, {self.lon}) {self.ts}"
