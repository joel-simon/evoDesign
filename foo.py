from os.path import join
import os
import argparse
import pickle

from examples.table.table import Table as Simulation

def main(args):
    path = args.dir
    best_genome = pickle.load(open(join(path, 'genome.p'), 'rb'))

    sim_params = []
    for Y in range(4, 16):
        for X in range(4, 9):
            Z = 16 - X
            sim_params.append({'bounds': (X, Y, Z)})

    for i, params in enumerate(sim_params):
        simulation = Simulation(best_genome, start=[(0, 0, 0)], **params)
        simulation.run()
        max_steps = simulation.max_fitness_steps
        simulation = Simulation(best_genome, **params)
        simulation.max_steps = max_steps + 1
        simulation.run(viewer=None)
        print(params, simulation.fitness())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    args = parser.parse_args()
    main(args)
