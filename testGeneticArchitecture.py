import numpy as np
import geneticArchitecture
from geneticArchitecture import pretty_print
import unittest

class ScVectorizerTest(unittest.TestCase):
	def ttest_crossover(self):
		l = 6
		X = (np.random.rand(2, l, l)*2).astype(int)
		# print X
		child1, child2 = geneticArchitecture.crossover(X[0], X[1])
		# print child1
		# print child2
		self.assertFalse(np.array_equal(X[0], child1))
		self.assertFalse(np.array_equal(X[1], child2))

	def test_distance_to_bathroom(self):
		X =  [[0,2,0,0,2],
					[2,1,2,0,0],
					[0,2,0,0,0],
					[0,2,2,1,2],
					[2,1,2,2,0]]
		# print geneticArchitecture.distances_to_bathrooms(np.array(X))
		self.assertEqual(1,1)

	def test_valid_elevator(self):
		X =  [[0,2,0,0,2],
					[2,1,2,0,0],
					[0,0,3,0,0],
					[0,0,2,1,2],
					[2,0,0,2,0]]
		isvalid = geneticArchitecture.valid_elevator(np.array(X))
		self.assertTrue(isvalid)
	
	def test_not_valid_elevator(self):
		X =  [[2,2,0,0,2],
					[2,1,2,0,0],
					[0,0,3,0,0],
					[0,0,2,1,2],
					[2,0,0,2,0]]
		isvalid = geneticArchitecture.valid_elevator(np.array(X))
		self.assertFalse(isvalid)

if __name__ == "__main__":
	unittest.main()
