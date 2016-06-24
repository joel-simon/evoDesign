import sys
import os
import pickle

from cellGenome import CellGenome
import numpy as np

pop = pickle.load(open('out/n100_mean5/population.p'))
best_genome = pop.statistics.best_genomes(10)[0]
print best_genome.fitness
del best_genome.fitness
print type(best_genome)
pickle.dump(best_genome, open('./out/n100_mean5/genome.p', 'w+'))
