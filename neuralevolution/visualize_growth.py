import pickle, os, sys
import numpy as np
import letters
from neat import nn
from simulate import simulate

def main(pickle_path):
	genome = pickle.load(open(pickle_path, 'rb' ))
	net    = nn.create_feed_forward_phenotype(genome)
	output = simulate(net, [8,8], letters.pretty_print)


if __name__ == '__main__':
  main(sys.argv[1])