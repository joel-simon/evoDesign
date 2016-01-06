from neat import nn, population, statistics, visualize
import pickle
import numpy as np
import letters

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def simulate(net, shape):
	world = np.zeros(shape)
	
	i_max = shape[0] - 1
	j_max = shape[1] - 1
	
	states = dict()
	world[i_max//2, j_max//2] = 1
	states[(i_max//2, j_max//2)] = {'has_replicated': 0}
	time_since_change = 0

	for _ in range(world.size*2):
		change = False
		where = np.where(world == 1)
		for i, j in zip(where[0], where[1]):
			state  = states[(i,j)]
			inputs = np.zeros([7])

			# neighbor above
			if i > 0 and world[i-1, j] == 1:     inputs[0] = 1
			# neighbor below
			if i < i_max and world[i+1, j] == 1: inputs[1] = 1
			# neighbor left
			if j > 0 and world[i, j-1] == 1:     inputs[2] = 1
			# neighbor right
			if j < j_max and world[i, j+1] == 1: inputs[3] = 1
			
			inputs[4] = i / i_max
			inputs[5] = j / j_max
			inputs[6] = states[(i,j)]['has_replicated']

			output = np.array(net.serial_activate(inputs))
			if output.max() > 0.5:
				change = True
				time_since_change = 0
				if np.argmax(output) == 4:
					world[i, j] = 0
					del states[(i, j)]
				else:
					i_d, j_d = directions[np.argmax(output)]
					if (i + i_d >= 0 and i + i_d < world.shape[0] and \
						j + j_d >= 0 and j + j_d < world.shape[1]):
						state['has_replicated'] = 1
						world[i+i_d, j+j_d] = 1
						states[(i+i_d, j+j_d)] = { 'has_replicated': 0 }
					
		if change == False:
			time_since_change += 1
			if time_since_change > 2:
				break


	return world

def eval_fitness_columns(genomes):
	for g in genomes:
		l = 6
		error = 0.0
		net   = nn.create_feed_forward_phenotype(g)
		world = simulate(net, l)
		g.fitness = (world[::2].sum()/world[::2].size) - (world[1::2].sum() / world[1::2].size)

def eval_fitness_letter(genomes, letter):
	for g in genomes:
		net   = nn.create_feed_forward_phenotype(g)
		world = simulate(net, letter.shape)

		correct   = np.logical_and(letter, world)
		incorrect = np.logical_and((1 - letter), world)

		# when perfect score is 1
		g.fitness = (correct.sum() - incorrect.sum()) / letter.sum()

def main():
	letter = letters.E
	fitness_fun = lambda genomes: eval_fitness_letter(genomes, letter)
	# fitness_fun = lambda genomes: eva(genomes)
	pop = population.Population('main_config')
	pop.epoch(fitness_fun, 100)

	print('Number of evaluations: {0}'.format(pop.total_evaluations))

	# Display the most fit genome.
	print('\nBest genome:')
	winner = pop.most_fit_genomes[-1]
	winner_net = nn.create_feed_forward_phenotype(winner)
	print(simulate(winner_net, [8,8]))
	print(simulate(winner_net, [16, 16]))
	print(simulate(winner_net, [32, 32]))
	# print(simulate(winner_net, 24))
	
	visualize.plot_stats(pop)
	visualize.plot_species(pop)
	visualize.draw_net(winner, view=True)
	statistics.save_stats(pop)
	statistics.save_species_count(pop)
	statistics.save_species_fitness(pop)
	

main()