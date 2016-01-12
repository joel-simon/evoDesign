from simulate import simulate
from truss_analysis import truss_from_map
import numpy as np
import math
shape     = (8,8)

def eval_fitness(genome):
	hex_map = simulate(genome, shape)[0]
	truss = truss_from_map(hex_map, 10)
	
	fitness = 0.0
	if hex_map.values.sum() < 2:
		return 0
	
	# 33% of fitness is getting to the top
	tallest_node = np.where(hex_map.values == 1)[0].max()
	fitness += (tallest_node / (hex_map.values.shape[0] -1)) / 3
	if fitness < .33: return fitness

	# 33% is covering top
	fitness += (hex_map.values[-1].sum()/ hex_map.values.shape[1]) / 3
	if fitness < .66: return fitness

	# 33% is optimization
	# try:
		# truss.calc_mass()
	truss.calc_fos()
	k = 10
	percent_occupied = hex_map.values.sum() / hex_map.values.size
	fitness += (((math.atan((truss.fos_total - 2) * 10) / math.pi) + 0.5) / (1+percent_occupied)) /3
	# except:
	# 	pass
	return fitness

def eval_fitnesses(genomes):
  # fitensses = pool.map(eval_fitness, genomes)
  # for fitness, genome in zip(fitensses, genomes):
  #   genome.fitness = fitness

	for genome in genomes:
		genome.fitness = eval_fitness(genome)
