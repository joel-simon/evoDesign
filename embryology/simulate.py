import math
import numpy as np
from neat import nn
from hexmap import Map

def get_input(hex_map, pheromone_maps, i, j):
	cell_inputs = []
		
	for n_i, occupied in enumerate(hex_map.occupied_neighbors((i, j))):
		if occupied != False:
			cell_inputs.append(1)
		else:
			cell_inputs.append(0)

	for p_map in pheromone_maps:
		cell_inputs.append(p_map.values[i, j])

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
		signal_map.values[i2, j2] += signal_strength(d, pheromone_gene)
	return

def cell_growth_cycle(genome, hex_map, pheromone_maps):
	# Create a network from the genome
	net = nn.create_feed_forward_phenotype(genome)
	change_made    = False
	occupied_cells = np.where(hex_map.values == 1)
	next_values    = hex_map.values.copy()
	activation_threshold = 0.75

	# update_pheromone_maps(pheromones, pheromone_maps)
	for p_gene, p_map in zip(genome.pheromone_genes, pheromone_maps):
		p_map.values *= p_gene.decay_gene.value

	for i, j in zip(occupied_cells[0], occupied_cells[1]):

		cell_input  = get_input(hex_map, pheromone_maps, i, j)
		cell_output = np.array(net.serial_activate(cell_input))

		output_grow = cell_output[:6]
		output_apop = cell_output[6]
		# output_pher = cell_output[7: 10]
		
		# Check for growth in any direction
		for (i_d, j_d), output in zip(hex_map.directions((i, j)), output_grow):
			if output > activation_threshold:
				valid    = hex_map.valid_cell((i+i_d, j+j_d))
				empty    = valid and (hex_map.values[i+i_d, j+j_d] == 0)
				if valid and empty:
					next_values[i+i_d, j+j_d] = 1
					change_made = True
		
		# Last output is cell death.
		if output_apop > activation_threshold:
			next_values[i, j] = 0
			change_made       = True
		
		# for i_p, output in enumerate(output_pher):
		# 	if cell_output[i_p] > activation_threshold:
		# 		add_signal(i, j, genome.pheromone_genes[i_p], pheromone_maps)

		# return next_values
		hex_map.values = next_values


def simulate(genome, shape, log = None):	
	# State values
	hex_map =  Map(shape, int)
	pheromone_maps = [ Map(shape) for i in range(genome.num_pheromones) ]
	
	# Start position is stored in attribute gene as floats
	attributes = [ a.value for a in genome.attribute_genes ]
	i_start = 0#int(attributes[0] * shape[0])
	j_start = 0#int(attributes[1] * shape[1])
	hex_map.values[i_start, j_start] = 1

	# Create a rough ceiling
	n_iterations = int((hex_map.rows * hex_map.cols))

	prev_values = []
	for i in range(n_iterations):
		
		if log != None:
			log(hex_map, i)

		cell_growth_cycle(genome, hex_map, pheromone_maps)
		prev_values.append(hex_map.values)
		if len(prev_values) > 3 and np.array_equal(prev_values[-1], prev_values[-3]):
			break
		if len(prev_values) > 3 and np.array_equal(prev_values[-1], prev_values[-4]):
			break
	
	if log != None:
		log(hex_map, i)

	return (hex_map, pheromone_maps)

