import pickle, os, sys
import numpy as np
import pygame
from neat import nn
from simulate import simulate

from visualize_truss import draw_truss
from fitness import eval_fitness, eval_fitnesses, eval_fos
from simulate import simulate
from truss_analysis import truss_from_map
from hexmap import Map

import time


pygame.init()
basicFont  = pygame.font.SysFont(None, 24)

size      = width, height = 1600, 1000
screen     = pygame.display.set_mode(size)
np.set_printoptions(linewidth=125, precision=2)

def plot_growth(hex_map, signals):
	truss   = truss_from_map(hex_map)
	draw_truss(screen, truss, 0)
	time.sleep(.4)

def main(pickle_path, i = 8, j = 8):
	genome  = pickle.load(open(pickle_path, 'rb' ))
	simulate(genome, (i, j), plot_growth)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()


if __name__ == '__main__':
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))