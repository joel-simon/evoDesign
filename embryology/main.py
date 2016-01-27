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
import cProfile

num_generations = 10
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

def main(checkpoint_path = None):
	run_parallel = False

	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	pop         = population.Population(config_path,
																			checkpoint_interval = None,
																			checkpoint_generation = 20)

	if os.path.exists('output'):
		erase = input('Delete existing output folder? (y/n) :')
		if erase == 'y':
			os.system("rm -rf output")
		else:
			print('aborting.')
			return
	
	os.makedirs('output')

	if checkpoint_path != None:
		pop.load_checkpoint(checkpoint_path)

	if run_parallel:
		pe = parallel.ParallelEvaluator(num_cores, eval_fitness)
		pop.epoch(pe.evaluate, num_generations, plot_genome)
	else:
		pop.epoch(eval_fitnesses, num_generations, plot_genome)

	# Display the most fit genome.
	print
	print('#'*80)
	print('Done')
	print('Best genome has fitness: ', pop.best_fitness_ever)
	print('#'*80)
	winner = pop.best_genome_ever

	visualize.plot_stats(pop, filename='output/avg_fitness.svg')
	visualize.plot_species(pop, filename='output/speciation.svg')
	visualize.draw_net(winner, view = False, filename='output/network')

	with open('output/best_genome.p', 'wb') as f:
		pickle.dump(winner, f)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
	else:
		main()
