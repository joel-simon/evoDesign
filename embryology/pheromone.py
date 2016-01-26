import math
# import np

class Pheromone(object):
	"""docstring for Pheromone"""
	def __init__(self, pos, pheromone_gene):
		self.i = pos[0]
		self.j = pos[1]
		self.type = pheromone_gene.ID
		self.strength = pheromone_gene.strength_gene.value
		self.decay    = pheromone_gene.decay_gene.value
		self.distance = pheromone_gene.distance_gene.value
		self.age   = 0
		self.max_dist = 4
		self.max_strength = 3

	def calc_strength(self, d):
		if self.distance == 0:
			return 0
		time_loss = math.exp(-self.decay * self.age)
		distance_loss = math.exp((-d**2)/(self.max_dist*self.distance))
		return self.strength * self.max_strength * distance_loss * time_loss
	
	# Signal map is a hexagon map
	def add_signal(self, signal_map):
		center = (self.i, self.j)
		for i2, j2 in signal_map.spread(center, self.max_dist+1):
			d = float(signal_map.distance(center, (i2, j2)))
			signal_map.values[i2, j2] += self.calc_strength(d)

		self.age += 1

if __name__ == '__main__':
	import numpy as np

	from hexmap import Map
	from neat.genes import PheromoneGene
	np.set_printoptions(linewidth=125, precision=2, suppress=True)
	signal_map = Map((8,8))
	# for i, j in signal_map.neighbors((4,4)):
	# 	signal_map.values[i, j] = 1

	pheromone_gene = PheromoneGene(1,2,3)
	pheromone = Pheromone((4,4), pheromone_gene)

	pheromone.add_signal(signal_map)
	# print(signal_map.values)
	signal_map.values[::] = 0
	pheromone.add_signal(signal_map)
	# print(signal_map.values)
	# print(signal_map.values)