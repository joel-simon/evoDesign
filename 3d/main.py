import sys, time, math
import numpy as np
from numpy.random import randint
from trussme import truss
from collections import Mapping, defaultdict

import warnings

# 
# pygame.init()
# size      = width, height = 640, 480
# screen    = pygame.display.set_mode(size)
# basicFont = pygame.font.SysFont(None, 24)
# BLACK     = (0,0,0)
# WHITE     = (255, 255, 255)

np.set_printoptions(precision = 1, linewidth=125, suppress=True)

def xy(coords):
	padding  = 5
	size = 50.0
	x = coords[0]*size + padding
	y = height - coords[1]*size - padding
	# y = height - (P.shape[0] - i -1)*size - padding
	return (int(x), int(y))

def draw(t1):
	screen.fill((255,255,255))
	
	for j_i, joint in enumerate(t1.joints):
		pygame.draw.circle(screen, BLACK, xy(joint.coordinates), 2)
		text = basicFont.render(str(j_i), True, (0, 0, 0), (255, 255, 255))
		textrect = text.get_rect()
		textrect.centerx = xy(joint.coordinates)[0]+10
		textrect.centery = xy(joint.coordinates)[1]
		screen.blit(text, textrect)

	for m in t1.members:
		a_xy = xy(m.joints[0].coordinates)
		b_xy = xy(m.joints[1].coordinates)

		text = basicFont.render(str(m.idx), True, (255, 0, 0), (255, 255, 255))
		textrect = text.get_rect()
		textrect.centerx = (b_xy[0] + a_xy[0])/2
		textrect.centery = (b_xy[1] + a_xy[1])/2
		screen.blit(text, textrect)

		if m.fos_yielding > 1:
			color = (0, 255, 0)
		else:
			color = ( int((1 - m.fos_yielding) * 255), int(m.fos_yielding * 255), 0)
		pygame.draw.line(screen, color, a_xy, b_xy, 2)
	pygame.display.flip()

def validate_truss(t):
	loads_total = np.zeros([1, 3])
	reactions_total = np.zeros([1, 3])
	for j in t.joints:
		reactions_total += j.reactions.T
		loads_total += j.loads.T

	# print('loads total', loads_total[0])
	# print('reactions total', reactions_total[0])
	# print('mass',t.mass*10)
	difference = loads_total[0][1] + reactions_total[0][1] - t.mass*10
	# print('difference', difference)
	# print(( + reactions_total[0])[1], reactions_total[0][1]*.01)
	return (difference < reactions_total[0][1]*.1)

def fos_score(fos):
	k = 10
	return (math.atan((fos - 1) * 10) / math.pi) + 0.5

def phenotype(x):
	# 0th level all stay	
	i = x.shape[0] -1
	front = set([(i,j) for j in x[i] if j])
	seen  = set()
	
	p = np.zeros(x.shape)
	while len(front) > 0:
		next_front = set()
		for (i, j) in front:
			p[i, j] = 1				
			if j > 0 and x[i, j-1]:              next_front.add((i, j-1))
			if j < x.shape[1] - 1 and x[i, j+1]: next_front.add((i, j+1))

			if i > 0 and x[i - 1, j]:              next_front.add((i-1, j))
			if i < x.shape[0] - 1 and x[i +1, j]: next_front.add((i+1, j))

		seen.update(front)
		next_front = next_front.difference(seen)
		front = next_front
	
	return p

def truss_from_X(x):
	t1 = truss.Truss()
	nodes = defaultdict()
	nodes.default_factory = nodes.__len__
	members = set()
	
	for i, j in np.ndindex(x.shape):
		if x[i, j]:
			nodes[(i,j)]
			nodes[(i+1,j)]
			nodes[(i,j+1)]
			nodes[(i+1,j+1)]

			members.add(((i,j), (i+1, j+1)))
			members.add(((i,j), (i+1, j)))
			members.add(((i,j), (i, j+1)))
			members.add(((i+1,j), (i+1, j+1)))
			members.add(((i,j+1), (i+1, j+1)))

	for ((i,j), n) in sorted(nodes.items(), key = lambda t: t[1]):
		if 5 - i == 0:
			t1.add_support(np.array([j, 5 - i, 0.0]), d=2)
		else:
			t1.add_joint(np.array([j, 5-i, 0.0]), d=2)

		# if i == 0:
		# 	t1.joints[-1].loads[1] = -300000

	for m_a, m_b in members:
		t1.add_member(nodes[m_a], nodes[m_b])

	return t1

def score(x):
	x = phenotype(x)
	t = truss_from_X(phenotype(x))
	
	max_y = x.shape[0]
	for j in t.joints:
		if j.coordinates[1] == max_y:
			j.loads[1] = -30000
	try:
		t.calc_mass()
		t.calc_fos()
	except:
		return [0, 0]

	mass = t.mass
	if mass == 0:
		return [0, t.fos_total]
	return [(1 / mass) * fos_score(t.fos_total) * x[0].sum(), t.fos_total]

def mutate(x, p):
	# n_m = max(int(np.random.normal(p, 1)), 0)
	# for m in range(n_m):
	i = randint(x.shape[0])
	j = randint(x.shape[1])
	x[i, j] = not x[i, j]
	return x

def pickCrossover(X, n):
	indexes = np.random.choice(np.arange(len(X)), n, replace = False)
	return X[np.sort(indexes)]

def crossover(x1, x2):
	shape  = x1.shape
	i0 = randint(0, shape[0])
	j0 = randint(0, shape[1])

	i1 = randint(i0, i0+shape[0])
	j1 = randint(j0, j0+shape[1])
	
	child1 = x1.copy()
	child2 = x2.copy()

	for i in range(i0, i1):
		for j in range(j0, j1):
				i_ = i % shape[0]
				j_ = j % shape[1]
				child1[i_, j_] = x2[i_, j_]
				child2[i_, j_] = x1[i_, j_]

	return [child1, child2]

def pick_top(n, X):
	scores  = np.array([score(x)[0] for x in X])
	top     = sorted(enumerate(scores), reverse = True, key = lambda k: k[1])
	indexes = [e[0] for e in top[:n]]
	return X[indexes]

def GA(X, p_c, iterations):	
	for i in range(iterations):
		n = int(len(X) * p_c)
		X1 = pick_top(n, X)
		
		to_crossover = pickCrossover(X, len(X) - n)
		crossed = []
		for j in range(0, len(to_crossover)-1, 2):
			crossed += crossover(to_crossover[j], to_crossover[j+1])

		X = np.concatenate((X1, crossed))
		
		for x in X:
			mutate(x, 3)

		if i % 5 == 0:
			print('current best', i, score(X1[0]))
			pretty_print(phenotype(X1[0]))

	return X1[0]

def pretty_print(x):
	colors = [ "\033[90m #", "\033[92m #", "\033[91m #", "\033[93m #"]
	fn = lambda i: colors[int(i)]
	for r in x:
		print(''.join(map(fn, r)))
	print("\033[00m")

def main():
	l = 6
	population = 100
	p_c = .4
	iterations = 1000
	# X = np.array([[1, 1, 1, 1, 0],
	# 							[1, 1, 1, 1, 0],
	# 							[0, 0, 0, 0, 0],
	# 							[1, 1, 1, 0, 0],
# # 							[1, 1, 1, 0, 0]])
	# X = np.array([[ 1.,1.,1.,1.,1.,1.],
	# 						 [ 1.,0.,1.,0.,0.,0.],
	# 						 [ 0.,0.,1.,0.,0.,1.],
	# 						 [ 1.,1.,1.,1.,0.,0.],
	# 						 [ 1.,1.,0.,1.,1.,0.],
	# 						 [ 1.,0.,0.,0.,0.,1.]])
	# print(phenotype(X))
	# print(score(X))
	# return
	# X = np.random.randint( 2, size = (population, l, l) )
	X = np.ones([population, l, l*2])

	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		best = GA(X, p_c, iterations)
	
	pretty_print(phenotype(best))

main()