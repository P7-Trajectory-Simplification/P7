from algorithms.great_circle_math import (
    great_circle_distance
)
from classes.route import Route
from classes.vessel_log import VesselLog
from classes.priority_queue import PriorityQueue
import numpy as np


def update_sed(index: int, trajectory: list[VesselLog], heap: PriorityQueue, succ: dict, pred: dict):
    if index in pred and index in succ:
        a = trajectory[pred[index]]
        b = trajectory[succ[index]]
        target = trajectory[index]
        
        if target.ts - a.ts < b.ts - target.ts:
            # Closer to a
            sed = np.abs(great_circle_distance(a.get_coords(), target.get_coords()))
        else:
            # Closer to b
            sed = np.abs(great_circle_distance(b.get_coords(), target.get_coords()))

        heap.insert(index, target, sed)
        



def squish(trajectory: list[VesselLog], buff: list[VesselLog], buff_size: int = 100):
    heap = PriorityQueue()
    succ = {}
    pred = {}

    for i in range(len(trajectory)):
        heap.insert(i, trajectory[i], float('inf'))

        if i > 0: #After the first point
            succ[i - 1] = i
            pred[i] = i - 1

        if heap.size() >= 3:
            update_sed(i-1, trajectory, heap, succ, pred)


        if heap.size() == buff_size + 1:
            index, _, _ = heap.remove_min()
            
            succ[pred[index]] = succ[index]
            pred[succ[index]] = pred[index]
            del pred[index]; del succ[index]

            if index in pred and index in succ:
                update_sed(pred[index], trajectory, heap, succ, pred)
                update_sed(succ[index], trajectory, heap, succ, pred)
    
    #The first point is the one with 0 predecessors
    start = next((pid for pid in pred if pred[pid] is None), 0)
    curr = start
    while curr is not None: #Add each point in order
        buff.append(trajectory[curr])
        curr = succ.get(curr)


def run_squish(route: Route, params: dict) -> Route:
    squish(route.trajectory, route.squish_buff, params["buff_size"])
    return Route(route.squish_buff)
