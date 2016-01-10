import pickle, os, sys
import numpy as np
import letters
from neat import nn, ctrnn
from simulate import simulate
import matplotlib.pyplot as plt

np.set_printoptions(linewidth=125, precision=2)

def print_signals(S):
	print(S)
	# for s in S:
	# 	colors = [ "\033[90m #", "\033[92m #", "\033[93m #", "\033[94m #", "\033[95m #", "\033[96m #"]
	# 	fn = lambda i: colors[int(i)]
	# 	for r in s:
	# 		print(''.join(map(fn, r % (len(colors)))))
	# 	print("\033[00m")


def plot_growth(output, signals):
	letters.pretty_print(output)
	print_signals(signals)

def main(pickle_path, i = 8, j = 8):
	genome = pickle.load(open(pickle_path, 'rb' ))
	net    = nn.create_feed_forward_phenotype(genome)
	attributes = [a.value for a in genome.attribute_genes]
	output     = simulate(net, [i,j], attributes, plot_growth)[0]

	# plt.matshow(1-output, cmap=plt.cm.gray)
	# plt.show()

	return True


if __name__ == '__main__':
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))