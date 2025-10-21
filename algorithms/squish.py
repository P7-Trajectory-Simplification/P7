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
    a_tuple = buff[index - 1].vessel_log.get_coords()
    b_tuple = buff[index + 1].vessel_log.get_coords()
    target_tuple = buff[index].vessel_log.get_coords()

    distance = None
    if a_tuple == b_tuple:
        # we can't make a great circle if the points are the same, so we just get the distance from one of the points to the target
        distance = great_circle_distance(
            a_tuple, target_tuple, radius=EARTH_RADIUS_METERS
        )
    else:
        # if the points are not the same, we find the distance from the target to the circle formed by A and B
        distance = point_to_great_circle(
            a_tuple, b_tuple, target_tuple, radius=EARTH_RADIUS_METERS
        )
    buff[index].sed = distance


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
