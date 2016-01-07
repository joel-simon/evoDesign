from neat import nn, population, statistics, visualize, parallel
import pickle, os
import numpy as np
import letters
from sklearn import metrics

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def valid_coordinates(i, j, X):
	if (i < 0 or i >= X.shape[0]): return False
	if (j < 0 or j >= X.shape[1]): return False
	return True

def simulate(net, shape):
	world            = np.zeros(shape)
	i_max, j_max     = (shape[0] - 1, shape[1] - 1)
	i_start, j_start = (0, 0)
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
			# print(cell_output)
			# check for growth in any of 4 directions
			for i_z in range(4):
				if cell_output[i_z] > np.random.rand():
					i_d, j_d = directions[i_z]
					valid    = valid_coordinates(i+i_d, j+j_d, world)
					empty    = valid and (world[i+i_d, j+j_d] == 0)
					if valid and empty:
						next_world[i+i_d, j+j_d] = 1
						cell_state['has_replicated'] = 1
						states[(i+i_d, j+j_d)] = { 'has_replicated': 0 }
						change_made       = True

			# output 5 is cell death
			if cell_output[4] > np.random.rand():
				next_world[i, j]  = 0
				change_made       = True
				del states[(i, j)]
		
		world = next_world
		
		if change_made == False:
			time_since_change += 1
			if time_since_change > 2:
				break
		else:
			time_since_change == 0


	return world

def eval_fitness_columns(genomes):
	for g in genomes:
		l = 6
		error = 0.0
		net   = nn.create_feed_forward_phenotype(g)
		world = simulate(net, l)
		g.fitness = (world[::2].sum()/world[::2].size) - (world[1::2].sum() / world[1::2].size)

def score(a, b):
	# correct   = np.logical_and(a, b)
	# incorrect = np.logical_and((1 - a), b)
	return metrics.accuracy_score(b.ravel(), a.ravel(), normalize = True)
	# return metrics.f1_score(a.ravel(), b.ravel())
	# 1 when identical
	# return (correct.sum() - incorrect.sum()) / b.sum()

def eval_fitness_letter(genome, letter=letters.L):
	net    = nn.create_feed_forward_phenotype(genome)
	output = simulate(net, letter.shape)

	return score(output, letter)

def log_best(genome):
	net    = nn.create_feed_forward_phenotype(genome)
	output = simulate(net, [8,8])
	letters.pretty_print(output)


def main():
	# print(score(letters.L, letters.L))
	# return
	# letter = letters.E
	# fitness_fun = lambda genomes: eval_fitness_letter(genomes, letter)
	pe = parallel.ParallelEvaluator(8, eval_fitness_letter)
	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	pop         = population.Population(config_path)
	pop.epoch(pe.evaluate, 100, log_best)
	# pop.epoch(eval_fitness_letter, 100, log_best)

	print('Number of evaluations: {0}'.format(pop.total_evaluations))

	# Display the most fit genome.
	print('\nBest genome:')
	winner = pop.most_fit_genomes[-1]
	winner_net = nn.create_feed_forward_phenotype(winner)
	letters.pretty_print(simulate(winner_net, [8,8]))
	letters.pretty_print(simulate(winner_net, [16, 16]))
	letters.pretty_print(simulate(winner_net, [32, 32]))
	# print(simulate(winner_net, [32, 32]))
	# print(simulate(winner_net, 24))
	
	visualize.plot_stats(pop)
	visualize.plot_species(pop)
	visualize.draw_net(winner, view=True)
	statistics.save_stats(pop)
	statistics.save_species_count(pop)
	statistics.save_species_fitness(pop)
	

if __name__ == '__main__':
    main()