import numpy as np
from simulate import simulate
from visualize import draw_hex_map
from hexmap import Map
from sklearn import metrics
import pygame

def filter_unconnected(hex_map, front):
	seen = set()
	
	filtered_hex_map = Map((hex_map.rows, hex_map.cols))

	while len(front) > 0:
		next_front = set()
		for (i, j) in front:
			filtered_hex_map.values[i, j] = hex_map.values[i, j]
			foo = [on for on in hex_map.occupied_neighbors((i, j)) if on != False ]
			next_front.update(foo)

		seen.update(front)
		next_front = next_front.difference(seen)
		front      = next_front

	return filtered_hex_map

class Experiment(object):
	
	def fitnesses(self, genomes):
		for genome in genomes:
			genome.fitness = self.fitness(genome)		
	
	def fitness(self, genome):
		hex_map = simulate(genome, self.shape)[0]
		y_true = np.ravel(self.target.values)
		y_pred = np.ravel(hex_map.values)

	def draw(self, genome):
		if self.screen != None:
			self.screen.fill((255,255,255))
			draw_hex_map(self.screen, self.grow(genome))
			pygame.display.flip()

# The front is the starting set that others must be connected to.



class SurfaceArea(Experiment):
	def __init__(self, shape, screen=None):
		self.shape  = shape
		self.screen = screen

	def surfaceArea(self, hexmap):
		surfaceArea = 0
		for index, v in np.ndenumerate(hexmap.values):
			if v != 0:
				neighbors = len(hexmap.neighbors(index))
				surfaceArea += neighbors - hexmap.num_occupied_neighbors(index)
		return surfaceArea

	def grow(self, genome):
		hexmap = simulate(genome, self.shape)[0]
		return filter_unconnected( hexmap, set([(0,0)]) )

	def fitness(self, genome):
		hexmap = self.grow(genome)
		surfaceArea = self.surfaceArea(hexmap)
		return surfaceArea / float(hexmap.values.size * 2)

class Truss(Experiment):
	def __init__(self, arg):
		self.arg = arg
	def draw(self, genome):
		pass
		# def plot_genome(genome):
# 	hex_map = simulate(genome, shape)[0]
# 	truss   = truss_from_map(hex_map, hex_radius)
# 	fitness = eval_fitness(genome)
# 	fos = None
# 	try:
# 		fos = eval_fos(truss)
# 	except:
# 		pass

# 	draw_truss(screen, truss, fitness, fos)

if __name__ == '__main__':
	hexmap = Map((4,4))
	# hexmap.values += 1
	hexmap.values[1,2] = 1
	hexmap.values[2,2] = 1
	print(hexmap)
	print(SurfaceArea((4,4), None).surfaceArea(hexmap))
