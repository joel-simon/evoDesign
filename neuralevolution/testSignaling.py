from neat import nn, population, statistics, visualize, parallel, ctrnn
from neat.config import Config
import os
import numpy as np
import letters
from sklearn import metrics
from simulate import simulate
from main import get_net

shape = [8,8]

def fitness(genome):
	net          = get_net(genome)
	signals      = np.zeros(shape)
	signals[0,0] = 1
	world, signals = simulate(net, shape, signals)
	i, j = np.where(signals > .5)
	if len(i) ==0:
		return 0
	m = max([a+b for a, b in zip(i, j)])
	# score   = (np.where(signals > 0)[0].max() + np.where(signals > 0)[1].max())/2
	score = m / 14
	return score

def log_best(genome):
	net          = get_net(genome)
	signals      = np.zeros(shape)
	signals[0,0] = 1
	world, signals = simulate(net, shape, signals)
	letters.pretty_print(world)
	print(signals.astype(int))

def main():
	num_generations = 10
	num_cores = 1

	pe = parallel.ParallelEvaluator(num_cores, fitness)
	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	config = Config(config_path)

	pop         = population.Population(config)
	pop.epoch(pe.evaluate, num_generations, log_best)

	# Display the most fit genome.
	print('\nBest genome:')
	winner = pop.most_fit_genomes[-1]
	log_best(winner)
	visualize.draw_net(winner, view=False)
main()