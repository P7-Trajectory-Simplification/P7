import itertools
import heapq

from classes.vessel_log import VesselLog


class PriorityQueue:
    def __init__(self):
        self.heap = []  # The heap list of entries
        # Maps point id to entries [float, int, VesselLog|string]
        self.entry_finder: dict[int, list[float | int | VesselLog | str]] = {}
        self.REMOVED = "<removed>"  # Placeholder for a removed point
        self.counter = itertools.count()  # Unique sequence count

        self.pred: dict[int, VesselLog | None] = {}  # Maps point id to its predecessor
        self.succ: dict[int, VesselLog | None] = {}  # Maps point id to its successor
        self.last: VesselLog | None = None

    def insert(self, point: VesselLog, priority=float('inf')):
        """Equivalent to 'set priority(Pi, priority, Q)'."""
        if point.id in self.entry_finder:  # Point already in the queue
            self.remove(point)  # Lazy removal
        else:
            if self.last is None:
                self.pred[point.id] = None  # No predecessor for the first point
            else:
                self.pred[point.id] = self.last  # Set predecessor
                self.succ[self.last.id] = point  # Set successor of the last point
                self.succ[point.id] = None  # No successor yet
            self.last = point
        count = next(self.counter)  # Unique sequence count
        entry = [priority, count, point]  # Create new entry
        self.entry_finder[point.id] = entry  # Add to entry finder
        heapq.heappush(self.heap, entry)  # Push onto the heap

    def remove_min(self) -> tuple[VesselLog, float]:
        """Equivalent to 'remove min(Q)'."""
        while self.heap:  # While there are entries in the heap
            priority, _, point = heapq.heappop(self.heap)  # Pop the smallest entry
            if point != self.REMOVED:  # If it's not a removed point
                if self.pred[point.id] is None or self.succ[point.id] is None:
                    raise RuntimeError("Cannot remove endpoint from priority queue")
                del self.entry_finder[point.id]  # Remove from entry finder

                self.succ[self.pred[point.id].id] = self.succ[
                    point.id
                ]  # Update successor of predecessor
                self.pred[self.succ[point.id].id] = self.pred[
                    point.id
                ]  # Update predecessor of successor

                del self.pred[point.id]  # Remove predecessor mapping
                del self.succ[point.id]  # Remove successor mapping

                return point, priority  # Return the point and its priority
        raise KeyError("pop from empty queue")  # If heap is empty

    def min_priority(self):
        """Equivalent to 'min priority(Q)'."""
        while self.heap:  # While there are entries in the heap
            priority, _, point = self.heap[0]  # Peek at the smallest entry
            if point == self.REMOVED:  # If it's a removed point
                heapq.heappop(self.heap)  # Remove it from heap
                continue  # Continue to next entry
            return priority  # Return the priority
        return float('inf')  # If heap is empty

    def remove(self, point: VesselLog):
        """Lazy removal helper."""
        entry = self.entry_finder.pop(point.id, None)  # Remove from entry finder
        if entry is not None:  # If entry exists
            entry[2] = self.REMOVED  # Mark as removed

    def size(self):
        return len(self.entry_finder)  # Number of active entries

    def to_list(self) -> list[VesselLog]:
        starts = [pid for pid, p in self.pred.items() if p is None]
        if len(starts) != 1:
            raise RuntimeError(
                f"Invalid predecessor structure. Expected 1 start, found {len(starts)}"
            )

        curr = starts[0]  # Start from the first point
        result = []

        visited = set()

        while curr is not None:
            if curr in visited:
                raise RuntimeError(f"Cycle detected at {curr}")
            visited.add(curr)
            entry = self.entry_finder.get(curr)
            if entry is None:
                raise RuntimeError(f"Missing entry_finder entry for id {curr}")

            result.append(entry[2])

            succ = self.succ.get(curr)
            if succ is None:
                break
            curr = succ.id

        return result
