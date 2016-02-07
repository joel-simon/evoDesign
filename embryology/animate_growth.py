import pickle, os, sys
import numpy as np
import pygame
from neat import nn
from simulate import simulate
import time
from truss_analysis import truss_from_map
from visualize import draw_truss
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
	time.sleep(.5)


def main(args):
	genome = pickle.load(open(args.path, 'rb'), encoding='latin1')
	shape  = (args.rows, args.cols)

	if os.path.exists(directory):
		os.system("rm -rf "+directory)
	os.makedirs(directory)
	simulate(genome, shape, plot_growth)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('path', type=str)
	parser.add_argument('rows', type=int, nargs='?', default=8)
	parser.add_argument('cols', type=int, nargs='?', default=8)

	main(parser.parse_args())