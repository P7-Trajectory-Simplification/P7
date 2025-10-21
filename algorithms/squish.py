from algorithms.great_circle_math import (
    point_to_great_circle,
    great_circle_distance,
    EARTH_RADIUS_METERS,
)
from classes.route import Route
from classes.squish_point import SquishPoint
from classes.vessel_log import VesselLog
import numpy as np


def update_sed(index: int, buff: list[SquishPoint]):
    a = buff[index - 1].vessel_log
    b = buff[index + 1].vessel_log
    target = buff[index].vessel_log
    
    if target.ts - a.ts < b.ts - target.ts:
        # Closer to a
        buff[index].sed = np.abs(great_circle_distance(a.get_coords(), target.get_coords()))
    else:
        # Closer to b
        buff[index].sed = np.abs(great_circle_distance(b.get_coords(), target.get_coords()))


def find_min_sed(buff: list[SquishPoint]) -> int:
    if len(buff) <= 2:
        return 0
    return min(range(1, len(buff) - 1), key=lambda i: buff[i].sed)


def squish(trajectory: list[VesselLog], buff: list[SquishPoint], buff_size: int = 100):
    for i in range(0, len(trajectory)):
        buff.append(SquishPoint(trajectory[i], float('inf')))
        buff_length = len(buff)
        if buff_length >= 3:
            update_sed(buff_length - 2, buff)
        if buff_length == buff_size:
            index = find_min_sed(buff)
            del buff[index]
            buff_length = len(buff)
            if 1 < index:
                update_sed(index - 1, buff)
            if index < buff_length - 1:
                update_sed(index, buff)


def run_squish(route: Route) -> Route:
    squish(route.trajectory, route.squish_buff)
    return Route(route.extract_squish_buffer())
