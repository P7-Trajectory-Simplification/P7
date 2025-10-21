import itertools
import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder = {}
        self.REMOVED = "<removed>"
        self.counter = itertools.count()

    def insert(self, point_id, point, priority=float('inf')):
        """Equivalent to 'set priority(Pi, priority, Q)'."""
        if point_id in self.entry_finder:
            self.remove(point_id)
        count = next(self.counter)
        entry = [priority, count, point_id, point]
        self.entry_finder[point_id] = entry
        heapq.heappush(self.heap, entry)

    def remove_min(self):
        """Equivalent to 'remove min(Q)'."""
        while self.heap:
            priority, _, point_id, point = heapq.heappop(self.heap)
            if point_id != self.REMOVED:
                del self.entry_finder[point_id]
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
