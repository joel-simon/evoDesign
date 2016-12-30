from itertools import product
from time import time
from multiprocessing import Pool

def loops():
	n = 200
	X, Y, Z = (n, n, n)

	start = time()
	for x in range(X):
		for y in range(Y):
			for z in range(Z):
				pass
	print 'manual loop', time() - start

	start = time()
	for x, y, z in product(range(X), range(Y), range(Z)):
		pass

	print 'product loop', time() - start
	start = time()

def multiprocessing():
	start = time()
	for i in range(100):
		pool = Pool(10)
		pool.close()
		pool.join()
	print time() - start

multiprocessing()
