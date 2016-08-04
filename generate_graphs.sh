#!/opt/local/bin/python
# !/usr/bin/python
from os.path import join, isfile
import sys
import os
import argparse
import pickle

from neat import visualize

def main(args):
    out_dir = args.dir

    if isfile(join(args.dir, 'winner.p')):
        with open(join(args.dir, 'winner.p'), 'rb') as f:
            best_genome = pickle.load(f)

        # print(best_genome.node_names)
        # Visualize the best network.
        # node_names = dict()
        # for n_id, node in best_genome.node_genes.items():
        #     if node.name != '':
        #         node_names[n_id] = str(node.name)
        #     else:
        #         node_names[n_id] = str(n_id)
        # print(node_names)
        # for i, name in enumerate(best_genome.inputs + best_genome.outputs):
        #     # Hack to deal with fact inputs are strings and outputs are tuples.
        #     if type(name) == type(tuple()):
        #         name = name[0]
        #     node_names[i] = name

        visualize.draw_net(best_genome,
                           view=False,
                           node_names=best_genome.node_names,
                           filename=join(args.dir,"nn_winner.gv"))

        print('Generated network graph.')

    if isfile(join(args.dir, 'population.p')):
        pop = pickle.load(open(join(args.dir, 'population.p'),'rb'))
        # Plot the evolution of the best/average fitness.
        visualize.plot_stats(pop.statistics, ylog=True,
                            filename=join(out_dir,"nn_fitness.svg"))

        # Visualizes speciation
        visualize.plot_species(pop.statistics,
                        filename=join(out_dir,"nn_speciation.svg"))

        print('Generated population graphs.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    args = parser.parse_args()
    main(args)
