from datetime import datetime
import numpy as np


class VesselLog:
    def __init__(self, lat: float, lon: float, ts: datetime, imo: int, id: int):
        self.lat = lat # Latitude of the log in degrees
        self.lon = lon # Longitude of the log in degrees
        self.ts = ts # Timestamp of the log in datetime
        self.imo = imo # IMO number of the vessel
        self.id = id # Id of the log in the database (auto incremented)

    def get_coords(self) -> tuple[float, float]:
        #Get the latitude and longitude in radians.
        return np.radians(self.lat), np.radians(self.lon)

    def strip_imo(self):
        #Delete the IMO from the VesselLog and free up the memory space.
        del self.imo

    def __repr__(self):
        #String representation of the VesselLog.
        return f"({self.lat}, {self.lon}) {self.ts}"
