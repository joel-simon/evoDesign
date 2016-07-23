#!/opt/local/bin/python
from os.path import join
import sys
import os
import argparse
import pickle

from neat import visualize

def main(args):
    out_dir = args.dir

    with open(join(args.dir, 'winner.p'), 'rb') as f:
        best_genome = pickle.load(f)

    # Visualize the best network.
    node_names = dict()
    for i, name in enumerate(best_genome.inputs + best_genome.outputs):
        node_names[i] = name

    visualize.draw_net(best_genome, view=False, node_names=node_names,
                    filename=join(args.dir,"nn_winner.gv"))
    print('Generated network graph.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    args = parser.parse_args()
    main(args)
