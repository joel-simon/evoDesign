import sys
import os
import argparse
import pickle
from neat import visualize

genome_path = '/Users/joelsimon/Projects/evoDesign/cppn/winner_genome.p'
population_path = '/Users/joelsimon/Projects/evoDesign/cppn/winner_population.p'

with open(genome_path, 'rb') as f:
    genome = pickle.load(f)

    node_names = {0: 'x', 1:'y', 2:'z', 3:'has_cell (sigmoid)'}

    for ID, gene in genome.node_genes.items():
        if ID > 3:
            node_names[ID] = "%s %i" % (gene.activation_type, ID)

    visualize.draw_net(genome,
                       # view=True,
                       show_disabled=False,
                       prune_unused=True,
                       node_names=node_names,
                       filename="cppn/nn_winner.gv")

    print('Generated network graph.')

with open(population_path, 'rb') as f:
    population = pickle.load(f)
    # Plot the evolution of the best/average fitness.
    visualize.plot_stats(population.statistics,
                         ylog=False,
                         filename="cppn/nn_fitness.svg")

    # Visualizes speciation
    visualize.plot_species(population.statistics,
                          filename="cppn/nn_speciation.svg")

    print('Generated population graphs.')
