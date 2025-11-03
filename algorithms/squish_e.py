import math

from algorithms.great_circle_math import great_circle_distance, EARTH_RADIUS_METERS
from classes.route import Route
from classes.squish_point import SquishPoint
from classes.vessel_log import VesselLog
from classes.priority_queue import PriorityQueue
import numpy as np


def adjust_priority(point_id: int, point: VesselLog, trajectory: list[VesselLog], heap: PriorityQueue, pred: dict, succ: dict, max_neighbor: dict):
    """
    Called when inserting and removing points and updates the priority (sed) of all of the neighboring points

    Parameters
    ---------
    point_id: int
        The ID of the point that has to be updated
    point: VesselLog
        The lat lon and time of the point
    trajectory: list[VesselLog]
        A list of all the raw data points that needs to be compressed
    heap: PriorityQueue
        A priority queue which sorts the items based on priority (sed)
    pred: dict
        Map storing, for each point ∈ heap, Points closest predecessor among the points in heap
    succ: dict
        Map storing, for each point ∈ heap, Points closest successor among the points in heap
    max_neighbor: dict
        Map storing, for each point ∈ heap, the maximum of the priorities that the neighboring    
        points had when they were removed from heap
    """

    if point_id in pred and point_id in succ: #Check if first or last point
        before = trajectory[pred[point_id]]
        after = trajectory[succ[point_id]]
        if point.ts - before.ts < after.ts - point.ts: #Find nearest point in time to compute sed (This is not entirely correct squish-e)
            priority = max_neighbor[point_id] + np.abs(great_circle_distance(point.get_coords(), before.get_coords()))
        else:
            priority = max_neighbor[point_id] + np.abs(great_circle_distance(point.get_coords(), after.get_coords()))
        heap.insert(point_id, point, priority)
        
def reduce(trajectory: list[VesselLog], heap: PriorityQueue, pred: dict, succ: dict, max_neighbor: dict):
    """
    Describes how the heap is reduced when the buffer size is full

    Parameters
    -----------
    trajectory: list[VesselLog]
        A list of all the raw data points that needs to be compressed
    heap: PriorityQueue
        A priority queue which sorts the items based on priority (sed)
    pred: dict
        Map storing, for each point ∈ heap, Points closest predecessor among the points in heap
    succ: dict
        Map storing, for each point ∈ heap, Points closest successor among the points in heap
    max_neighbor: dict
        Map storing, for each point ∈ heap, the maximum of the priorities that the neighboring    
        points had when they were removed from heap
    """

    id, _, priority = heap.remove_min()

    max_neighbor[succ[id]] = max(priority, max_neighbor[succ[id]])
    max_neighbor[pred[id]] = max(priority, max_neighbor[pred[id]])

    succ[pred[id]] = succ[id] #register succ[Pj] as the closest successor of pred[Pj]
    pred[succ[id]] = pred[id] #register pred[Pj] as the closest predecessor of succ[Pj]

    #Adjust neighboring points
    adjust_priority(pred[id], trajectory[pred[id]], trajectory, heap, pred, succ, max_neighbor)
    adjust_priority(succ[id], trajectory[succ[id]], trajectory, heap, pred, succ, max_neighbor)

    #Garbage Collection
    del pred[id]; del succ[id]; del max_neighbor[id]

def squish_e (trajectory: list[VesselLog], buff: list[VesselLog], low_comp_rate: float, up_bound_sed: float, buff_size: int = 4):
    """
    Implementation of the SQUISH-E algorithm, which is a trajectory simplification algorithm that works like SQUISH
    It implements an adaptable buffer and ensures all the points are at least of a certain importance

    Parameters
    --------------
    trajectory: list[VesselLog]
        A list of all the raw data points that needs to be compressed
    buff: list[VesselLog]
        The final storage list for the finished simplified trajectory
    low_comp_rate: float
        The lower bound compression rate, should never be 0. 
        If = 1, SQUISH-E only simplifies based on SED error
    up_bound_sed: float
        The upper bound SED error, if = 0, SQUISH-E only cares about compression rate.
    """
    heap = PriorityQueue()
    pred = {}
    succ = {}
    max_neighbor = {}

    for i in range(0, len(trajectory)):
        buff_size = max(4, math.floor((i+1) / low_comp_rate) + 1)

        heap.insert(i, trajectory[i], float('inf')) #Insert point with priority = inf
        max_neighbor[i] = 0

        if i > 0: #After the first point
            succ[i - 1] = i
            pred[i] = i - 1
            adjust_priority(i-1, trajectory[i-1], trajectory, heap, pred, succ, max_neighbor) #update priority
        #TODO: Use Peter's function for size instead
        if len(heap.entry_finder) == buff_size: #Reduce buffer when full
            reduce(trajectory, heap, pred, succ, max_neighbor)
    
    #After finishing looping through, keep reducing heap until all points satisfies upper bound on SED
    while heap.min_priority() <= up_bound_sed:
        reduce(trajectory, heap, pred, succ, max_neighbor)
    
    #The first point is the one with 0 predecessors
    start = next((pid for pid in pred if pred[pid] is None), 0)
    curr = start
    while curr is not None: #Add each point in order
        buff.append(trajectory[curr])
        curr = succ.get(curr)


def run_squish_e(route: Route, params: dict) -> Route:
    squish_e(route.trajectory, route.squish_e_buff, params["low_comp"], params["max_sed"], 4)
    return Route(route.squish_e_buff)