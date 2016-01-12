from neat import nn, population, statistics, visualize, parallel, ctrnn
from neat.config import Config
import pickle, os
import numpy as np
import math

import sys
from simulate import simulate
from truss_analysis import truss_from_map
from hexmap import Map
import multiprocessing

import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

from visualize_truss import draw_truss

from fitness import eval_fitness, eval_fitnesses

num_generations = 100
num_cores = 8
shape     = (8,8)
size      = width, height = 500, 500
hex_radius = 30

pygame.init()
basicFont  = pygame.font.SysFont(None, 24)
screen     = pygame.display.set_mode(size)

def plot_genome(genome):
	hex_map = simulate(genome, shape)[0]
	truss   = truss_from_map(hex_map, 30)
	draw_truss(screen, truss, hex_radius)

def main():

	pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())
	# pe = parallel.ParallelEvaluator(num_cores, eval_fitness)
	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	pop = population.Population(config_path)
	

	# pop.epoch(pe.evaluate, num_generations, None)
	pop.epoch(eval_fitnesses, num_generations, plot_genome)

	# Display the most fit genome.
	print()
	print('Done')
	print('Best genome has fitness: ', pop.best_fitness_ever)
	winner = pop.best_genome_ever
	
	# plot_genome(winner)
	# plot_genome(winner, [16, 16])
	# plot_genome(winner, [32, 32])
	
	visualize.plot_stats(pop)
	visualize.plot_species(pop)
	visualize.draw_net(winner, view=False)

	with open(os.path.join(local_dir, 'best_genome.p'), 'wb') as f:
		pickle.dump(winner, f)

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

if __name__ == '__main__':
	main()