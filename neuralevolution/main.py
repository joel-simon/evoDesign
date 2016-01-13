from neat import nn, population, statistics, visualize, parallel, ctrnn
from neat.config import Config
import pickle, os
import numpy as np
import math
import sys
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

from visualize_truss import draw_truss
from fitness import eval_fitness, eval_fitnesses, eval_fos
from simulate import simulate
from truss_analysis import truss_from_map
from hexmap import Map

num_generations = 1
num_cores = 32
shape     = (12,16)
hex_radius = 5
size      = width, height = 800, 800


pygame.init()
basicFont  = pygame.font.SysFont(None, 24)
screen     = pygame.display.set_mode(size)

def plot_genome(genome):
	hex_map = simulate(genome, shape)[0]
	truss   = truss_from_map(hex_map, hex_radius)
	fitness = eval_fitness(genome)
	fos = None
	try:
		fos = eval_fos(truss)
	except:
		pass

	draw_truss(screen, truss, fitness, fos)

def test():
	hex_map = Map((12, 16))
	hex_map.values += 1
	# hex_map.values[0,0] = 1
	# hex_map.values[0,1] = 1
	# hex_map.values[1,1] = 1

	# hex_map.values[3,0] = 1
	# hex_map.values[3,2] = 1

	# hex_map.values[0,6] = 1
	# hex_map.values[1,6] = 1

	# hex_map.values[2,5] = 1
	# hex_map.values[2,7] = 1

	# print(hex_map.ascii())

	from simulate import filter_unconnected
	hex_map = filter_unconnected(hex_map)
	truss = truss_from_map(hex_map)
	draw_truss(screen, truss, 0)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

def main(checkpoint_path = None):
	run_parallel = False

	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	pop = population.Population(config_path)

	if config_path != None:
		pop.load_checkpoint(checkpoint_path)

	if run_parallel:
		pe = parallel.ParallelEvaluator(num_cores, eval_fitness)
		pop.epoch(pe.evaluate, num_generations, plot_genome)
	else:
		pop.epoch(eval_fitnesses, num_generations, plot_genome)

	# Display the most fit genome.
	print()
	print('Done')
	print('Best genome has fitness: ', pop.best_fitness_ever)
	winner = pop.best_genome_ever

	visualize.plot_stats(pop)
	visualize.plot_species(pop)
	visualize.draw_net(winner, view=False)

	with open(os.path.join(local_dir, 'best_genome.p'), 'wb') as f:
		pickle.dump(winner, f)
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()


if __name__ == '__main__':
	main(sys.argv[1])
