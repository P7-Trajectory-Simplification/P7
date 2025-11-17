import itertools
import heapq

from classes.vessel_log import VesselLog


class PriorityQueue:
    def __init__(self):
        self.heap = [] # The heap list of entries
        # Maps point id to entries [float, int, VesselLog|string]
        self.entry_finder: dict[int, list[float | int | VesselLog | str]] = {}
        self.REMOVED = "<removed>" # Placeholder for a removed point
        self.counter = itertools.count() # Unique sequence count

        self.pred: dict[int, VesselLog] = {} # Maps point id to its predecessor
        self.succ: dict[int, VesselLog] = {} # Maps point id to its successor

    def insert(self, point: VesselLog, priority=float('inf')):
        """Equivalent to 'set priority(Pi, priority, Q)'."""
        if point.id in self.entry_finder: # Point already in the queue
            self.remove(point) # Lazy removal
        count = next(self.counter) # Unique sequence count
        entry = [priority, count, point] # Create new entry
        self.entry_finder[point.id] = entry # Add to entry finder
        heapq.heappush(self.heap, entry) # Push onto the heap

    def remove_min(self) -> tuple[VesselLog, float]:
        """Equivalent to 'remove min(Q)'."""
        while self.heap: # While there are entries in the heap
            priority, _, point = heapq.heappop(self.heap) # Pop the smallest entry
            if point != self.REMOVED: # If it's not a removed point
                del self.entry_finder[point.id] # Remove from entry finder

                self.succ[self.pred[point.id].id] = self.succ[point.id] # Update successor of predecessor
                self.pred[self.succ[point.id].id] = self.pred[point.id] # Update predecessor of successor

                del self.pred[point.id] # Remove predecessor mapping
                del self.succ[point.id] # Remove successor mapping

                return point, priority # Return the point and its priority
        raise KeyError("pop from empty queue") # If heap is empty

    def min_priority(self):
        """Equivalent to 'min priority(Q)'."""
        while self.heap: # While there are entries in the heap
            priority, _, point = self.heap[0] # Peek at the smallest entry
            if point == self.REMOVED: # If it's a removed point
                heapq.heappop(self.heap) # Remove it from heap
                continue # Continue to next entry
            return priority # Return the priority
        return float('inf') # If heap is empty

    def update_priority(self, point: VesselLog, new_priority: float):
        """Equivalent to 'adjust priority' operation."""
        if point.id in self.entry_finder: # If point is in the queue
            _, _, point = self.entry_finder[point.id] # Get the existing point
            self.insert(point, new_priority) # Re-insert with new priority

    def remove(self, point: VesselLog):
        """Lazy removal helper."""
        entry = self.entry_finder.pop(point.id, None) # Remove from entry finder
        if entry is not None: # If entry exists
            entry[2] = self.REMOVED # Mark as removed

    def size(self):
        return len(self.entry_finder) # Number of active entries

    def to_list(self) -> list[VesselLog]:
        trajectory_list = [] # List to hold the trajectory points
        start = next((pid for pid in self.pred if self.pred[pid] is None), 0) # Find the start point (no predecessor)
        curr = start # Start from the first point
        while curr is not None:  # Add each point in order
            trajectory_list.append(self.entry_finder[curr][2]) # Append current point
            curr = self.succ.get(curr) # Move to the successor
        return trajectory_list # Return the ordered list of points
