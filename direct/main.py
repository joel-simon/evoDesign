import sys, time, math
import numpy as np

import multiprocessing
import warnings

import score, model
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

def pretty_print(x):
	"""
	0 : Black
	1 : Green
	2 : Yellow
	3 : Red
	4 : Empty
	"""
	# 91 = red
	colors = [ "\033[90m x", "\033[92m x", "\033[93m <", "\033[93m v", "\033[90m  "]
	fn = lambda i: colors[int(i)]
	for r in x:
		print(''.join(map(fn, r)))
	print("\033[00m")

def pickCrossover(X, n):
	indexes = np.random.choice(np.arange(len(X)), n, replace = False)
	return X[np.sort(indexes)]

def pick_top(n, X, pool, mask):
	masks   = [mask for _ in range(len(X))]
	foo     = list(zip(masks, map(model.phenotype, X)))
	scores  = pool.map(score.score, foo)
	top     = sorted(enumerate(scores), reverse = True, key = lambda k: k[1])
	indexes = [e[0] for e in top[:n]]
	return X[indexes]

def GA(X, p_c, iterations, pool, mask):	
	for i in range(iterations):
		# Number to bring to next generation
		n  = int(len(X) * p_c)
		X1 = pick_top(n, X, pool, mask)
		
		to_crossover = pickCrossover(X, len(X) - n)
		crossed = []
		for j in range(0, len(to_crossover)-1, 2):
			crossed += model.crossover(to_crossover[j], to_crossover[j+1])

		X = np.concatenate((X1, crossed))
		
		for x in X:
			model.mutate(x, mask, 3)

		if i % 50 == 0:
			print('current best', i, score.score_and_fos(mask, X1[0]))
			pretty_print(model.phenotype(X1[0]))

	return X1[0]

def initial_population(population, mask):
	ratio_on = 7
	size     = (population, mask.shape[0], mask.shape[1])
	X        = np.random.randint(ratio_on, size = size).astype(bool).astype(int)
	
	for (i, j), v in np.ndenumerate(mask):
		if v > 0:
			X[:, i, j] = 1
		elif v == -1:
			X[:, i, j] = 0

	return X

def main():
	population = 96
	p_c = .4
	iterations = 2000
	w = 16
	h = 16
	mask = np.zeros([w, h])
	mask[:h/2, w/2:]   = -1 #blocked regions
	mask[:h/2, w/2-1]  = 2 #forced on
	mask[h/2, w/2-1:]  = 3 #forced on


	X = initial_population(population, mask)
	# pretty_print(X[-1])
	# print(X[0])
	# print(score.score_and_fos(mask, model.phenotype(X[0])))
	# return
	pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())
	# pretty_print
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		best = GA(X, p_c, iterations, pool, mask)
	
	pretty_print(model.phenotype(best))

main()