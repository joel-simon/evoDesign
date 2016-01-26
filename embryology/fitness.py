from simulate import simulate
from truss_analysis import truss_from_map
import numpy as np
import math
shape     = (12,16)

def eval_fos(truss):
	truss.calc_fos()
	fos_forward = truss.fos_total
		
	# change direction of x loads
	for joint in truss.joints:
		if abs(joint.loads[0]) > 0:
			joint.loads[0] *= -1
	truss.calc_fos()
	fos_reverse = truss.fos_total

	return (fos_forward + fos_reverse) / 2.0

def eval_fitness(genome):
	hex_map = simulate(genome, shape)[0]
	truss = truss_from_map(hex_map, 5)
	fitness = 0.0

	if hex_map.values.sum() < 2:
		return 0
	
	# 25% of fitness is getting to the top
	tallest_node = np.where(hex_map.values == 1)[0].max()
	fitness += (tallest_node / float(hex_map.values.shape[0] -1)) / 4.0
	if fitness < .25: return fitness

	# 25% is covering top
	fitness += (hex_map.values[-1].sum() / float(hex_map.values.shape[1])) / 4.0
	if fitness < .50: return fitness

	# 50% is optimization
	try:
		k = 10
		fos = eval_fos(truss)
		percent_occupied = hex_map.values.sum() / float(hex_map.values.size)
		fitness += (((math.atan((fos - 1) * k) / math.pi) + 0.5) * (1-percent_occupied)) / 2.0
	except:
	 	pass
	return fitness

def eval_fitnesses(genomes):
	for genome in genomes:
		genome.fitness = eval_fitness(genome)
