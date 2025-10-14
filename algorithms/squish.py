from algorithms.great_circle_math import point_to_great_circle, EARTH_RADIUS_METERS
from vessel_log import VesselLog
import numpy as np

def update_sed(index: int, buff: list):
    a_tuple = buff[index - 1][0].get_coords()
    b_tuple = buff[index + 1][0].get_coords()
    target_tuple = buff[index][0].get_coords()
        
    buff[index][1] = np.abs(point_to_great_circle(a_tuple, b_tuple, target_tuple, radius=EARTH_RADIUS_METERS))


def find_min_sed(buff: list[(VesselLog, float)]) -> int:
    if len(buff) <= 2:
        return 0
    return min(range(1, len(buff) - 1), key=lambda i: buff[i][1])


def squish(points: list[VesselLog], buff: list, buff_size: int = 100):
    for i in range(0, len(points)):
        buff.append([points[i], float('inf')])
        length = len(buff)
        if length >= 3:
            update_sed(length-2, buff)
        if length == buff_size:
            index = find_min_sed(buff)
            del buff[index]
            length = len(buff)
            if 1 < index:
                update_sed(index-1, buff)
            if index < length - 1:
                update_sed(index, buff)