from itertools import repeat
from copy import copy
import numpy
from multiprocessing import Pool
import itertools
import time
import pickle
from main import Experiment

from src.neat_custom.config import Config as NeatConfig
import operator
from prettytable import PrettyTable

from experiments.tree import Simulation, genome_config

experiment_config = {
    'generations': 50,
    'cores': 1,
    'pop_size': 50
}

def process_wrapper(params):
    """ pool.map can only pass one variable to each process.
        decontruct it and run the experiment, returning score
    """
    simulation, neat_config = params
    experiment = Experiment(simulation, genome_config, neat_config)
    pop = experiment.run(**experiment_config)
    genome = pop.statistics.best_genome()
    return genome.fitness

def parallel_batch(neat_config, n, c):
    pool = Pool(c)
    params = repeat((Simulation, neat_config), n)
    result = numpy.array(pool.map(process_wrapper, params))
    pool.close()
    pool.join()
    return result

if __name__ == '__main__':
    neat_config = NeatConfig('experiments/tree_config.txt')
    neat_config.report = False


    n = 1
    c = 6

    search_params = {
        'initial_connection': ['fully_connected', 'partial 0.75', 'partial 0.5', 'partial 0.25'],
        # 'initial_connection': ['unconnected', 'partial .25', 'partial .5',
        #                      'partial .75',  'fs_neat', 'fully_connected'],
        # 'hidden_nodes': [0],#range(0, 17, 4),
        # 'compatibility_threshold': [1.2]#[.6, .8, 1, 1.2],#[.1, .2, .3, .4, .5]
        # 'elitism': [1, 2, 4, 8, 16],
        # 'survival_threshold': [.05, .1, .2, .4]
    }
    # x = PrettyTable(search_params.keys() + ['mean_score', 'std']+)

    N = reduce(operator.mul, map(len, search_params.values()), 1)

    for i, params in enumerate(itertools.product(*search_params.values())):
        if i % 10 == 0 or N < 10:
            print i, '/', N

        for attr, param in zip(search_params.keys(), params):
            setattr(neat_config, attr, param)

        F = parallel_batch(neat_config, n=n, c=c)

        print params
        print str(F.mean())+'\t'+str(F.std())
        print '#' * 80
        # print '\t'.join(map(strF.std(axis=1))
        # print F.mean(), F.std()

        # scores.append((F.mean(), F.std(), params))

    # pickle.dump((search_params.keys(), scores), open('scores5.p', 'wb'))

    # for mean, std, params in list(sorted(scores, reverse=True))[:25]:
    #     x.add_row([mean, std]+list(params))

    print genome_config['modules']
    print experiment_config
    # print x
