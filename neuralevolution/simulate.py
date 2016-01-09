import math
import numpy as np
from neat import nn

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def valid_coordinates(i, j, X):
	if (i < 0 or i >= X.shape[0]): return False
	if (j < 0 or j >= X.shape[1]): return False
	return True

def get_input(world, signals, i, j):
	i_max, j_max     = (world.shape[0] - 1, world.shape[1] - 1)
	cell_inputs = np.zeros([22])
	# neighbor above
	if i > 0 and world[i-1, j] == 1:     cell_inputs[0] = 1
	# neighbor below
	if i < i_max and world[i+1, j] == 1: cell_inputs[1] = 1
	# neighbor left
	if j > 0 and world[i, j-1] == 1:     cell_inputs[2] = 1
	# neighbor right
	if j < j_max and world[i, j+1] == 1: cell_inputs[3] = 1
	
	scale_i = world.shape[0] / 8
	scale_j = world.shape[1] / 8
	cell_inputs[4 + int(i / scale_i)] = 1#i / i_max
	cell_inputs[12 + int(j / scale_j)] = 1#j / j_max

	cell_inputs[20] = signals[0, i, j]
	cell_inputs[21] = signals[1, i, j]
	return cell_inputs

def simulate(net, shape, start, log=None):
	world            = np.zeros(shape)
	last_world       = None
	signals          = np.zeros([2, shape[0], shape[1]])
	i_max, j_max     = (shape[0] - 1, shape[1] - 1)
	i_start, j_start = start

	states            = dict()
	time_since_change = 0
	iterations = int(world.size / 2)	

	world[i_start, j_start]    = 1
	states[(i_start, j_start)] = [0]*4 # {'has_replicated': 0, 'data': 0}
	# iterations_run = 0
	for iterations_run in range(iterations):
		change_made = False
		cells       = np.where(world == 1)
		next_world  = world.copy()

		for i, j in zip(cells[0], cells[1]):
			# cell_state  = states[(i,j)]
			cell_input  = get_input(world, signals, i, j)
			cell_output = np.array(net.serial_activate(cell_input))
			
			# check for growth in any of 4 directions
			for i_z in range(4):
				if cell_output[i_z] > 0.75:#np.random.rand():
					i_d, j_d = directions[i_z]
					valid    = valid_coordinates(i+i_d, j+j_d, world)
					empty    = valid and (world[i+i_d, j+j_d] == 0)
					if valid and empty:
						next_world[i+i_d, j+j_d] = 1
						# cell_state['has_replicated'] = 1
						states[(i+i_d, j+j_d)] = [0]*4
						change_made       = True
			
			# last output is cell death
			if cell_output[4] > 0.75:#np.random.rand():
				next_world[i, j]  = 0
				change_made       = True
				del states[(i, j)]

			signals[0, i, j] += cell_output[5]
			if j > 0:
				signals[0, i, j-1] += cell_output[5]
			if j < j_max:
				signals[0, i, j+1] += cell_output[5]

			if i > 0:
				signals[0, i-1, j] += cell_output[5]
			if i < i_max:
				signals[0, i+1, j] += cell_output[5]

			signals[1, i, j] += cell_output[6]
			if j > 0:
				signals[1, i, j-1] += cell_output[6]
			if j < j_max:
				signals[1, i, j+1] += cell_output[6]

			if i > 0:
				signals[1, i-1, j] += cell_output[6]
			if i < i_max:
				signals[1, i+1, j] += cell_output[6]

		if np.array_equal(next_world, last_world):
			break

		last_world = world
		world      = next_world
		signals *= .8
		
		if log != None:
			log(world)
			print(signals)

		if change_made == False:
			time_since_change += 1
			if time_since_change > 2:
				break
		else:
			time_since_change == 0


	return world, signals, iterations_run