import itertools
import heapq

from classes.vessel_log import VesselLog


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder = {}
        self.REMOVED = "<removed>"
        self.counter = itertools.count()
        self.predecessor = {}
        self.successor = {}

    def insert(self, point_id, point, priority=float('inf')):
        """Equivalent to 'set priority(Pi, priority, Q)'."""
        if point_id in self.entry_finder:
            self.remove(point_id)
        count = next(self.counter)
        entry = [priority, count, point_id, point]
        self.entry_finder[point_id] = entry
        heapq.heappush(self.heap, entry)

        if point_id > 0:  # After the first point
            self.successor[point_id - 1] = point_id
            self.predecessor[point_id] = point_id - 1

    def remove_min(self):
        """Equivalent to 'remove min(Q)'."""
        while self.heap:
            priority, _, point_id, point = heapq.heappop(self.heap)
            if point_id != self.REMOVED:
                del self.entry_finder[point_id]

                self.successor[self.predecessor[point_id]] = self.successor[point_id]
                self.predecessor[self.successor[point_id]] = self.predecessor[point_id]
                del self.predecessor[point_id]
                del self.successor[point_id]

                return point_id, point, priority
        raise KeyError("pop from empty queue")

    def min_priority(self):
        """Equivalent to 'min priority(Q)'."""
        while self.heap:
            priority, _, point_id, point = self.heap[0]
            if point_id == self.REMOVED:
                heapq.heappop(self.heap)
                continue
            return priority
        return float('inf')

    def update_priority(self, point_id, new_priority):
        """Equivalent to 'adjust priority' operation."""
        if point_id in self.entry_finder:
            _, _, _, point = self.entry_finder[point_id]
            self.insert(point_id, point, new_priority)

    def remove(self, point_id):
        """Lazy removal helper."""
        entry = self.entry_finder.pop(point_id, None)
        if entry is not None:
            entry[2] = self.REMOVED

    def size(self):
        return len(self.entry_finder)

    def get_points(self, trajectory: list[VesselLog]) -> list[VesselLog]:
        points = []
        # The first point is the one with 0 predecessors
        start = next((pid for pid in self.predecessor if self.predecessor[pid] is None), 0)
        curr = start
        while curr is not None:  # Add each point in order
            points.append(trajectory[curr])
            curr = self.successor.get(curr)
        return points