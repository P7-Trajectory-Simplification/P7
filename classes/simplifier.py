from abc import ABC


# this is an abstract class with the job of holding a trajectory (which is a list of VesselLogs)
# and providing a simplify()-method to be overridden by specific simplification algorithms
class Simplifier(ABC):  # "ABC" means it's an abstract class
    def __init__(self):
        self.trajectory = []

    def simplify(self):
        """Simplify the current trajectory in-place and return a description of the changes made to it.
        Must be overridden by derived classes."""
        raise NotImplementedError


# The description needs to be as compact as possible, since we need to send one for each request for each route.
# Conceptual description example:
# [5, 7, (50.31, 10.564), 3, (51.242, 11.193)]
# This says
# . remove point at index 5
# . remove point at index 7
# . append point (50.31, 10.564)
# . remove point at index 3
# . append point (51.242, 11.193)
# in that order.
# (We know to remove a point if the element is a single integer,
# otherwise we know to append the point described by the pair)
# We can pack the descriptions into a dictionary that maps the ID of the route to the description,
# so we can deal with multiple routes at once.
