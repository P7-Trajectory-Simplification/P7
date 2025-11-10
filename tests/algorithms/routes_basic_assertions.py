import unittest

from classes.route import Route


class BasicAssertions(unittest.TestCase):
    def __init__(self, route: Route, simplified_route: Route):
        super().__init__()

        trajectory = route.trajectory
        simplified_trajectory = simplified_route.trajectory

        self.assertLessEqual(len(simplified_trajectory), len(trajectory), "Simplified route should have fewer or equal points")
        self.assertEqual(simplified_trajectory[0], trajectory[0], "First point should remain the same")
        self.assertEqual(simplified_trajectory[-1], trajectory[-1], "Last point should remain the same")

        original = {p.get_coords() for p in trajectory}
        simplified = {p.get_coords() for p in simplified_trajectory}
        self.assertTrue(simplified.issubset(original), "Simplified trajectory must contain only original points.")
        self.assertIsInstance(simplified_route, Route, "Simplified route should return a Route instance.")


if __name__ == '__main__':
    unittest.main()
