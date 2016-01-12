import math
import numpy as np
from neat import nn
from hexmap import Map
from utilities import makeGaussian

directions = [ ( 0, 1 ), ( 1, 1 ), ( 1, 0 ), ( 0, -1 ), ( -1, -1 ), ( -1, 0 ) ]

def get_input(hex_map, signals, i, j):
	cell_inputs = np.zeros([24])
		
	for n_i, occupied in enumerate(hex_map.occupied_neighbors((i, j))):
		if occupied != False:
			cell_inputs[n_i] = 1
	
	scale_i = hex_map.rows / 8
	scale_j = hex_map.cols / 8
	cell_inputs[6 + int(i / scale_i)]  = 1
	cell_inputs[14 + int(j / scale_j)] = 1

	cell_inputs[22] = signals[0, i, j]
	cell_inputs[23] = signals[1, i, j]
	return cell_inputs

def filter_unconnected(hex_map):
	# i_max = hex_map.rows - 1
	front = set([(0, c) for c, v in enumerate(hex_map.values[0]) if v > 0 and c %2 == 0])
	seen  = set()
	
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

def simulate(genome, shape, log=None):
	net        = nn.create_feed_forward_phenotype(genome)
	attributes = [a.value for a in genome.attribute_genes]
	
	hex_map          = Map(shape)
	prev_values      = None
	signals          = np.zeros([2, shape[0], shape[1]])
	i_max, j_max     = (shape[0] - 1, shape[1] - 1)
	
	i_start = int(attributes[0]*shape[0])
	j_start = int(attributes[1]*shape[1])

	# signal_1_x = int(attributes[2] * 3)
	# signal_1_y = int(attributes[3] * 3)
	signal_1_mag = attributes[4]

	# signal_2_x = int(attributes[5] * 3)
	# signal_2_y = int(attributes[6] * 3)
	signal_2_mag = attributes[7]

	time_since_change = 0
	iterations = hex_map.rows * hex_map.cols

	hex_map.values[i_start, j_start] = 1
	
	for iterations_run in range(iterations):
		change_made    = False
		occupied_cells = np.where(hex_map.values == 1)
		next_values    = hex_map.values.copy()

		for i, j in zip(occupied_cells[0], occupied_cells[1]):
			cell_input  = get_input(hex_map, signals, i, j)
			cell_output = np.array(net.serial_activate(cell_input))
			
			# check for growth in any of 4 directions
			for i_z in range(6):
				if cell_output[i_z] > 0.75:#np.random.rand():
					i_d, j_d = directions[i_z]
					valid    = hex_map.valid_cell((i+i_d, j+j_d))
					empty    = valid and (hex_map.values[i+i_d, j+j_d] == 0)
					if valid and empty:
						next_values[i+i_d, j+j_d] = 1
						change_made = True
			
			# last output is cell death
			if cell_output[6] > 0.75:
				next_values[i, j] = 0
				change_made       = True
			
			for nei_row, nei_col in hex_map.neighbors((i, j)):
				signals[0, nei_row, nei_col] += cell_output[7]
				signals[1, nei_row, nei_col] += cell_output[8]
			# signals[0, i-signal_1_x:i+signal_1_x, j-signal_1_y:j+signal_1_y] += 1
			# signals[1, i-signal_2_x:i+signal_2_x, j-signal_2_y:j+signal_2_y] += 1

		if np.array_equal(next_values, prev_values):
			break

		prev_values    = hex_map.values
		hex_map.values = next_values
		signals *= .5
		
		# if log != None:
		# 	log(hex_map.values, signals)

		if change_made == False:
			time_since_change += 1
			if time_since_change > 2:
				break
		else:
			time_since_change == 0


	return filter_unconnected(hex_map), signals, iterations_run
