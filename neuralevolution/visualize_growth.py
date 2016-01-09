import pickle, os, sys
import numpy as np
import letters
from neat import nn, ctrnn
from simulate import simulate

np.set_printoptions(linewidth=125)

def get_start(genome):
	start = [int(g.value) for g in genome.attribute_genes[:2]]
	return start

def plot_genome(genome, size = (8,8)):
	net   = nn.create_feed_forward_phenotype(genome)
	output, signals, iterations_run = simulate(net, size, get_start(genome))
	print(get_start(genome))
	print(iterations_run)
	letters.pretty_print(output)
	print(signals.astype(int))

def main(pickle_path, i = 8, j = 8):
	genome = pickle.load(open(pickle_path, 'rb' ))
	net    = nn.create_feed_forward_phenotype(genome)
	output = simulate(net, [i,j], get_start(genome), letters.pretty_print)
	return True

if __name__ == '__main__':
  main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))