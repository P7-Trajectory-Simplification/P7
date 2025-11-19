# import unittest
# from app import index, get_algorithms

# class RequestTest(unittest.TestCase):
#     def test_index(self):
#         with app.test_client() as client:
#             response = client.get('/')
#             self.assertEqual(response.status_code, 200)
#             self.assertIn(b'Vessel Trajectory Simplification API', response.data)

#     def test_get_algorithms(self):
#         with app.test_client() as client:
#             response = client.get('/algorithms')
#             self.assertEqual(response.status_code, 200)
#             data = response.get_json()
#             self.assertIsInstance(data, list)
#             self.assertIn('Douglas-Peucker', data)  # Example algorithm name


# if __name__ == '__main__':
#     unittest.main()
