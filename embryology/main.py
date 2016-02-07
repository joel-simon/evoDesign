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
	parallel = False
	draw = True

	if draw:
		pygame.init()
		basicFont  = pygame.font.SysFont(None, 24)
		screen     = pygame.display.set_mode((800, 800))
	else:
		screen = None

	if os.path.exists('output'):
		# erase = input('Delete existing output folder? (y/n) :')
		if True:#erase == 'y':
			os.system("rm -rf output")
		else:
			print('aborting.')
			return		
	os.makedirs('output')

	experiment = experiments.SurfaceArea((8,8), screen)
	final_population = run_experiment(experiment, generations, parallel)

	best_genomes = final_population.best_genomes(5)
	winner = best_genomes[0]
	
	visualize.plot_stats(final_population, filename='output/avg_fitness.svg')
	visualize.plot_species(final_population, filename='output/speciation.svg')
	visualize.draw_net(winner, view = False, filename='output/network')

	with open('output/best_genomes.p', 'wb') as f:
		pickle.dump(best_genomes, f)

	with open('output/best_genome.p', 'wb') as f:
		pickle.dump(winner, f)

	# print([(experiment.fitness(genome), genome.fitness) for genome in best_genomes])

	print
	print('#'*80)
	print('saved best score', winner.fitness)
	print('average score', sum([bg.fitness for bg in best_genomes])/5.0)
	print('#'*80)

	if draw:
		experiment.draw(winner)
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

if __name__ == '__main__':
	main(sys.argv[1:])
