from os.path import join
import os
import argparse
import pickle

# import matplotlib.pyplot as plt
import numpy as np

from examples.table.table import Table as Simulation

def main(args):
    path = args.dir
    best_genome = pickle.load(open(join(path, 'genome.p'), 'rb'))

    sim_params = []

    y_bounds = range(4, 8)#24)
    x_bounds = range(4, 8)#12)

    results = np.zeros((len(y_bounds), len(x_bounds)))

    for i, Y in enumerate(y_bounds):
        for j, X in enumerate(x_bounds):
            Z = 16 - X
            params = {'bounds': (X, Y, Z)}
            # sim_params.append({'bounds': (X, Y, Z)})

    # for i, params in enumerate(sim_params):
            simulation = Simulation(best_genome, start=[(0, 0, 0)], **params)
            simulation.run()
            max_steps = simulation.max_fitness_steps
            simulation = Simulation(best_genome, **params)
            simulation.max_steps = max_steps + 1
            simulation.run(viewer=None)
            fitness = simulation.fitness()
            # print(params, fitness)
            results[i, j] = fitness

    # print(results)
    # plt.imshow(results, cmap=plt.cm.Blues, interpolation='nearest')
    # plt.show()
            # print(params, simulation.fitness())
    pickle.dump(results, open(join(path, 'test_results.p'), 'wb'))
    print('done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    args = parser.parse_args()
    main(args)
