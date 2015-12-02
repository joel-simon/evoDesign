import numpy as np
import itertools, random
from numpy.random import randint
np.set_printoptions(linewidth = 200)

"""
0 - empty
1 - bathroom
2 - desk
3 - elevator
4 - divider
"""
rooms = {
	'empty': 0,
	'bathroom': 1,
	'desk': 2,
	'elevator': 3
	# 'divider': 3
}
bathroom_cost = 1
weights = [1,1,1]

def get_score(x):
	if not valid_elevator(x):
		return np.inf

	number_of_bathrooms = (x == rooms['bathroom']).sum()
	number_of_desks = (x == rooms['desk']).sum()
	return distances_to_bathrooms(x) + number_of_bathrooms*.4 - number_of_desks*.2
	# n_bathrooms = (x == 1).sum()

	# score  = (n_bathrooms * bathroom_cost) * weights[0]
	# score += mean_walk_distance * weights[1]
	# score += mean_paths_per_time * weights[2]

	# return score

def get_neighbours(x, i, j):
	results = []
	if i > 0:          results.append((i-1, j))
	if i < x.shape[0]-1: results.append((i+1, j))
	
	if j > 0:          results.append((i, j-1))
	if j < x.shape[1]-1: results.append((i, j+1))
	
	return results

def valid_elevator(x):
	front = set([(x.shape[0]/2, x.shape[0]/2)])
	seen  = set()
	desks = set()
	while len(front) != 0:
		next_front = set()
		for (i, j) in front:
			seen.add((i,j))

			if x[i,j] == rooms['desk']:
				desks.add((i, j))

			if (x[i, j] == rooms['empty']) or (x[i, j] == rooms['elevator']):
				next_front.update(get_neighbours(x, i, j))
		next_front = next_front.difference(seen)
		front = next_front

	return len(desks) == (x == rooms['desk']).sum()
		
def distances_to_bathrooms(x):
	front = set()
	seen  = set()

	costs = [] # Cost matrix

	x2 = np.zeros_like(x, dtype = float) + np.inf
	
	for i, j in np.ndindex(x.shape):
		if x[i, j] == 1:
			x2[i, j] = 0
			# Set union in place
			seen.update((i,j))
			front.update(get_neighbours(x2, i, j))
			front.difference_update(seen)

	c = 1
	while len(front) != 0:
		next_front = set()
		for (i, j) in front:
			if x2[i, j] > c: 
				x2[i, j] = c
			seen.add((i,j))
			if x[i, j] == rooms['empty']:
				next_front.update(get_neighbours(x2, i, j))
		front = next_front.difference(seen)
		c += 1
	
	for i, j in np.ndindex(x.shape):
		if x[i, j] == rooms['desk']:
			costs.append(x2[i, j])

	return np.mean(costs)

def mutate(x, p):
	n_m = max(int(np.random.normal(p, 1)), 0)
	for m in xrange(n_m):
		i = randint(x.shape[0])
		j = randint(x.shape[1])
		if x[i, j] != rooms['elevator']:
			x[i, j] = randint(len(rooms)- 1)
	return x

def crossover(x1, x2):
	i0 = randint(0, x1.shape[0])
	j0 = randint(0, x1.shape[1])
	i1 = randint(0, x1.shape[0])
	j1 = randint(0, x1.shape[1])
	
	child1 = x1.copy()
	child2 = x2.copy()

	for i in xrange(min(i0, i1), max(i0,i1)):
		for j in xrange(min(j0, j1), max(j0, j1)):
			child1[i, j] = x2[i, j]
			child2[i, j] = x1[i, j]

	return [child1, child2]

def pick_top(n, X, score_func):
	scores = np.array([score_func(x) for x in X])
	top = sorted(enumerate(scores), reverse = False, key = lambda k: k[1])
	indexes = [e[0] for e in top[:n]]
	return X[indexes]

def pretty_print(x):
	colors = ["\033[90m #", "\033[91m #", "\033[92m #", "\033[93m #"]
	fn = lambda i: colors[i]
	for r in x:
		print ''.join(map(fn, r))
	print "\033[00m"

def makeBest():
	X = np.zeros([l,l]).astype(int) + rooms['desk']
	for i in xrange(1, l, 2):
		for j in xrange(0, l, 2):
			X[i, j] = rooms['bathroom']

	# for i in xrange(3, l, 4):
	# 	for j in xrange(3, l, 4):
	# 		X[i, j] = rooms['bathroom']

	return X

def pickCrossover(X, n):
	indexes = np.random.choice(np.arange(len(X)), n, replace = False)
	return X[np.sort(indexes)]

l = 20
population = 200
p_c = .4
iterations = 200

def GA(X, iterations):
	for i in xrange(iterations):
		n = int(len(X) * p_c)
		X1 = pick_top(n, X, get_score)
		
		to_crossover = pickCrossover(X, len(X) - n)
		crossed = []
		for j in xrange(0, len(to_crossover)-1, 2):
			crossed += crossover(to_crossover[j], to_crossover[j+1])

		X = np.concatenate((X1, crossed))
		
		for x in X:
			mutate(x, 1)

		if i % 20 == 0:
			print i, get_score(X1[0])
	return X1[0]

def get_initial(n):
	X = np.zeros([n, l, l]).astype(int)
	for x in X:
		x[l/2, l/2] = rooms['elevator']
	# return (np.random.rand(population, l, l)*len(rooms) - 1).astype(int)
	return X

def main():
	X = get_initial(population)

	best = GA(X, iterations)
	# print best
	pretty_print(best)

	print 'score:', get_score(best)
	print 'iterations', iterations
	print 'average distances to bathroom:', distances_to_bathrooms(best)
	print 'number of bathrooms:', (best == rooms['bathroom']).sum()
	print 'number of desks:', (best == rooms['desk']).sum()
	# def format():

if __name__ == "__main__":
	main()
