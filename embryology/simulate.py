import math
# import numpy as np
import copy
from neat import nn, ctrnn
from neat.genes import NodeGene
from hexmap import Map

def get_input(hex_map, pheromone_maps, i, j):
	cell_inputs = []
		
	for n_i, occupied in enumerate(hex_map.occupied_neighbors((i, j))):
		if occupied != False:
			cell_inputs.append(1)
		else:
			cell_inputs.append(0)

	for p_map in pheromone_maps:
		cell_inputs.append(p_map.values[i][j])

	return cell_inputs

def signal_strength(d, pheromone_gene):
	max_dist = 5
	max_strength = 4
	strength = pheromone_gene.strength_gene.value
	decay    = pheromone_gene.decay_gene.value
	distance = pheromone_gene.distance_gene.value
	if distance == 0:
		return 0

	distance_loss = math.exp((-d**2)/(max_dist*distance))
	return strength * max_strength * distance_loss

def add_signal(i, j, pheromone_gene, signal_maps):
	max_dist = 4
	signal_map = signal_maps[pheromone_gene.ID]
	center = (i, j)
	for i2, j2 in signal_map.spread(center, max_dist+1):
		d = float(signal_map.distance(center, (i2, j2)))
		signal_map.values[i2][j2] += signal_strength(d, pheromone_gene)
	return

def cell_growth_cycle(make_cell, hex_map, pheromone_maps):	
	next_values = [copy.copy(row) for row in hex_map.values]
	activation_threshold = 0.75

	# update_pheromone_maps(pheromones, pheromone_maps)
	# for p_gene, p_map in zip(genome.pheromone_genes, pheromone_maps):
	# 	p_map.values *= p_gene.decay_gene.value

	for i in range(hex_map.rows):
		for j in range(hex_map.cols):
			
			cell = hex_map.values[i][j]
			if isinstance(cell, ctrnn.Network):
				cell_input  = get_input(hex_map, pheromone_maps, i, j)
				
				cell_output = cell.parallel_activate(cell_input)
				# cell_output = cell.serial_activate(cell_input)

				output_grow = cell_output[:6]
				output_apop = cell_output[6]
				# output_pher = cell_output[7: 10]
				
				# Check for growth in any direction
				for (i_d, j_d), output in zip(hex_map.directions((i, j)), output_grow):
					if output > activation_threshold:
						valid    = hex_map.valid_cell((i+i_d, j+j_d))
						empty    = valid and (hex_map.values[i+i_d][j+j_d] == 0)
						
						if valid and empty:
							next_values[i+i_d][j+j_d] = make_cell()
				
				# Last output is cell death.
				if output_apop > activation_threshold:
					next_values[i][j] = 0
				
				# for i_p, output in enumerate(output_pher):
				# 	if cell_output[i_p] > activation_threshold:
				# 		add_signal(i, j, genome.pheromone_genes[i_p], pheromone_maps)

	hex_map.values = next_values


def simulate(genome, shape, log = None, start=None):
	# State values
	hex_map = Map(shape) if start == None else start 
	pheromone_maps = [ Map(shape) for i in range(genome.num_pheromones) ]
	
	# net = nn.create_feed_forward_phenotype(genome)
	# make_cell = lambda: net
	
	make_cell = lambda: ctrnn.create_phenotype(genome)

	# Start position is stored in attribute gene as floats
	# attributes = [ a.value for a in genome.attribute_genes ]
	
	i_start = 0#int(attributes[0] * shape[0])
	j_start = 0#int(attributes[1] * shape[1])
	hex_map.values[i_start][j_start] = make_cell()
	# Create a rough ceiling
	n_iterations = int((hex_map.rows * hex_map.cols) / 2)

	prev_values = set()
	for i in range(n_iterations):
		
		if log != None:
			log(hex_map, i)

		cell_growth_cycle(make_cell, hex_map, pheromone_maps)
		string_repr = str(hex_map)

		if string_repr in prev_values:
			break
		else:
			prev_values.add(string_repr)

	if log != None:
		log(hex_map, i)

	return (hex_map, pheromone_maps)

if __name__ == '__main__':
	import sys, pickle
	genome = pickle.load(open(sys.argv[1], 'rb'), encoding='latin1')
	shape  = (12, 12)


	simulate(genome, shape)
