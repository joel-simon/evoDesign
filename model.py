import numpy as np


def crossover(x1, x2):
	shape  = x1.shape
	i0 = np.random.randint(0, shape[0])
	j0 = np.random.randint(0, shape[1])

	i1 = np.random.randint(i0, i0+shape[0])
	j1 = np.random.randint(j0, j0+shape[1])
	
	child1 = x1.copy()
	child2 = x2.copy()

	for i in range(i0, i1):
		for j in range(j0, j1):
			i_ = i % shape[0]
			j_ = j % shape[1]
			child1[i_, j_] = x2[i_, j_]
			child2[i_, j_] = x1[i_, j_]

	return [child1, child2]

def mutate(x, mask, p):	
	i = np.random.randint(x.shape[0])
	j = np.random.randint(x.shape[1])

	# Values greater than 1 signify forced on.
	# -1 signifies forced off.
	while mask[i, j] > 1 or mask[i, j] == -1:
		i = np.random.randint(x.shape[0])
		j = np.random.randint(x.shape[1])
		
	x[i, j] = not x[i, j]
	return x

def phenotype(x):
	# bottom level all stay	
	i = x.shape[0] - 1
	front = set([(i,j) for j,v in enumerate(x[i]) if v > 0])
	seen  = set()

	p = np.zeros(x.shape)

	while len(front) > 0:
		next_front = set()
		for (i, j) in front:
			p[i, j] = x[i, j]
			if j > 0 and x[i, j-1] > 0:             next_front.add((i, j-1))
			if j < x.shape[1] - 1 and x[i, j+1] >0: next_front.add((i, j+1))

			if i > 0 and x[i - 1, j] > 0:            next_front.add((i-1, j))
			if i < x.shape[0] - 1 and x[i +1, j] >0: next_front.add((i+1, j))

		seen.update(front)
		next_front = next_front.difference(seen)
		front      = next_front

	return p
