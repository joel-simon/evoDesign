import pickle, os, sys
import numpy as np
import pygame
from neat import nn
from simulate import simulate

from visualize_truss import draw_truss
from simulate import simulate
from hexmap import Map


pygame.init()
basicFont  = pygame.font.SysFont(None, 24)

size   = width, height = 800, 800
screen = pygame.display.set_mode(size)
np.set_printoptions(linewidth=125, precision=2)

directory = 'temp_images/'

def plot_growth(hex_map, signals, iteration):
	truss   = truss_from_map(hex_map)
	draw_truss(screen, truss)
	pygame.image.save(screen, directory + str(iteration)+'.jpg')

def main(pickle_path, i = 8, j = 8):
	print(i, j)
	genome  = pickle.load(open(pickle_path, 'rb'), encoding='latin1')


	if os.path.exists(directory):
		os.system("rm -rf "+directory)
	os.makedirs(directory)
	simulate(genome, (i, j), plot_growth)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()


if __name__ == '__main__':
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))