import numpy as np
from neat import nn

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def valid_coordinates(i, j, X):
	if (i < 0 or i >= X.shape[0]): return False
	if (j < 0 or j >= X.shape[1]): return False
	return True

def simulate(net, shape, log=None):
	world            = np.zeros(shape)
	i_max, j_max     = (shape[0] - 1, shape[1] - 1)
	i_start, j_start = (0, 0)
	# i_start, j_start = (i_max//2, j_max//2)
	# i_start, j_start = (np.random.randint(i_max), np.random.randint(j_max))
	states           = dict()
	time_since_change = 0
	iterations = world.size

	world[i_start, j_start]    = 1
	states[(i_start, j_start)] = {'has_replicated': 0}
	
	for _ in range(iterations):
		change_made = False
		cells       = np.where(world == 1)
		next_world  = world.copy()

		for i, j in zip(cells[0], cells[1]):
			cell_state  = states[(i,j)]
			cell_inputs = np.zeros([7])

			# neighbor above
			if i > 0 and world[i-1, j] == 1:     cell_inputs[0] = 1
			# neighbor below
			if i < i_max and world[i+1, j] == 1: cell_inputs[1] = 1
			# neighbor left
			if j > 0 and world[i, j-1] == 1:     cell_inputs[2] = 1
			# neighbor right
			if j < j_max and world[i, j+1] == 1: cell_inputs[3] = 1
			
			cell_inputs[4] = i / i_max
			cell_inputs[5] = j / j_max
			cell_inputs[6] = cell_state['has_replicated']

			cell_output = np.array(net.serial_activate(cell_inputs))

			# check for growth in any of 4 directions
			for i_z in range(4):
				if cell_output[i_z] > 0.5:#np.random.rand():
					i_d, j_d = directions[i_z]
					valid    = valid_coordinates(i+i_d, j+j_d, world)
					empty    = valid and (world[i+i_d, j+j_d] == 0)
					if valid and empty:
						next_world[i+i_d, j+j_d] = 1
						cell_state['has_replicated'] = 1
						states[(i+i_d, j+j_d)] = { 'has_replicated': 0 }
						change_made       = True

			# output 5 is cell death
			if cell_output[4] > 0.5:#np.random.rand():
				next_world[i, j]  = 0
				change_made       = True
				del states[(i, j)]
		
		world = next_world
		
		if log != None:
			log(world)

		if change_made == False:
			time_since_change += 1
			if time_since_change > 2:
				break
		else:
			time_since_change == 0


	return world