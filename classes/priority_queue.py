import itertools
import heapq

from classes.vessel_log import VesselLog


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder: dict[int, list[float | int | VesselLog | str]] = {}
        self.REMOVED = "<removed>"
        self.counter = itertools.count()

        self.pred: dict[int, VesselLog] = {}
        self.succ: dict[int, VesselLog] = {}

    def insert(self, point: VesselLog, priority=float('inf')):
        """Equivalent to 'set priority(Pi, priority, Q)'."""
        if point.id in self.entry_finder:
            self.remove(point)
        count = next(self.counter)
        entry = [priority, count, point]
        self.entry_finder[point.id] = entry
        heapq.heappush(self.heap, entry)

    def remove_min(self) -> tuple[VesselLog, float]:
        """Equivalent to 'remove min(Q)'."""
        while self.heap:
            priority, _, point = heapq.heappop(self.heap)
            if point != self.REMOVED:
                del self.entry_finder[point.id]

                self.succ[self.pred[point.id].id] = self.succ[point.id]
                self.pred[self.succ[point.id].id] = self.pred[point.id]

                del self.pred[point.id]
                del self.succ[point.id]

                return point, priority
        raise KeyError("pop from empty queue")

    def min_priority(self):
        """Equivalent to 'min priority(Q)'."""
        while self.heap:
            priority, _, point = self.heap[0]
            if point == self.REMOVED:
                heapq.heappop(self.heap)
                continue
            return priority
        return float('inf')

    def update_priority(self, point: VesselLog, new_priority: float):
        """Equivalent to 'adjust priority' operation."""
        if point.id in self.entry_finder:
            _, _, point = self.entry_finder[point.id]
            self.insert(point, new_priority)

    def remove(self, point: VesselLog):
        """Lazy removal helper."""
        entry = self.entry_finder.pop(point.id, None)
        if entry is not None:
            entry[2] = self.REMOVED

    def size(self):
        return len(self.entry_finder)