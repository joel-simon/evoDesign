#!/usr/bin/python
from os.path import join, isfile
import sys
import os
import argparse
import pickle
import matplotlib
from neat import visualize

def main(args):
    out_dir = args.dir

    if isfile(join(args.dir, 'genome.p')):
        with open(join(args.dir, 'genome.p'), 'rb') as f:
            best_genome = pickle.load(f)

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
