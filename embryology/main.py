from neat import nn, population, statistics, visualize, parallel, ctrnn
from neat.config import Config
import pickle, os
import numpy as np
import sys
import pygame
from simulate import simulate
from truss_analysis import truss_from_map
from hexmap import Map
import experiments

num_cores = 32
hex_radius = 5

pygame.init()
basicFont  = pygame.font.SysFont(None, 24)
screen     = pygame.display.set_mode((800, 800))

# def plot_genome(genome):
# 	hex_map = simulate(genome, shape)[0]
# 	truss   = truss_from_map(hex_map, hex_radius)
# 	fitness = eval_fitness(genome)
# 	fos = None
# 	try:
# 		fos = eval_fos(truss)
# 	except:
# 		pass

# 	draw_truss(screen, truss, fitness, fos)

def run_experiment(experiment, generations, parallel=False):
	pop = population.Population('main_config', checkpoint_interval = None,
																						 checkpoint_generation = None)
	if parallel:
		pe = parallel.ParallelEvaluator(num_cores, experiment.fitness)
		pop.epoch(pe.evaluate, generations, experiment.draw)
	else:
		pop.epoch(experiment.fitnesses, generations, experiment.draw)

	return pop

def main(args):
	generations = int(args[0])

	if os.path.exists('output'):
		# erase = input('Delete existing output folder? (y/n) :')
		if True:#erase == 'y':
			os.system("rm -rf output")
		else:
			print('aborting.')
			return		
	os.makedirs('output')

	experiment = experiments.ColumnsTarget((8,8), screen)
	final_population = run_experiment(experiment, generations, parallel=False)

	winner = final_population.best_genome_ever
	visualize.plot_stats(final_population, filename='output/avg_fitness.svg')
	visualize.plot_species(final_population, filename='output/speciation.svg')
	visualize.draw_net(winner, view = False, filename='output/network')

	with open('output/best_genome.p', 'wb') as f:
		pickle.dump(winner, f)

	print
	print('#'*80)
	print('Done')
	print('Best genome has fitness: ', final_population.best_fitness_ever)
	print('#'*80)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	main(sys.argv[1:])
