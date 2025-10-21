from algorithms.great_circle_math import point_to_great_circle, EARTH_RADIUS_METERS
from classes.route import Route
from classes.squish_point import SquishPoint
from classes.vessel_log import VesselLog

def set_priority():

def adjust_priority():
    

def squish_e (trajectory: list[VesselLog], buff: list[SquishPoint], low_comp_rate: float, up_bound_sed: float, buff_size: int = 4) -> list[VesselLog]:
    pred = {}
    succ = {}
    max_neighbor = {}

    for i in range(0,trajectory):
        if i/low_comp_rate >= buff_size:
            buff_size += 1
        
        set_priority(trajectory[i], 'inf', )

        if i > i:
            succ[i - 1] = trajectory[i]
            pred[i] = trajectory[i - 1]
            adjust_priority(trajectory[i-1], heap, pred, succ, pi)

        if len(heap) == buff_size:
