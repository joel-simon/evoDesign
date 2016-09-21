from itertools import repeat
from copy import copy
import numpy
from multiprocessing import Pool
import itertools
import time
import pickle
from main import Experiment
from experiments.shapes import E,O,R,Y,X,stripes,loops,dots,checkerboard,circles
from experiments.shapes import genome_config as base_shape_config

from src.neat_custom.config import Config as NeatConfig
import operator
from src.modules import neighbors_continuous, divide_theta, neighbors_distinct, \
                        divide_distinct, morphogen
from src.modules.signals import signal_0, signal_1, signal_2, signal_3, signal_4
shapes = [E,O,R,Y,X,stripes,loops,dots,checkerboard,circles]
shape_names = ['E','O','R','Y','X','stripes','loops','dots','checkerboard','circles']

# shapes = [R]
# shape_names = ['R']

def process_wrapper(params):
    """ pool.map can only pass one variable to each process.
        decontruct it and run the experiment, returning score
    """
    shape, neat_config, modules = params
    base_shape_config['modules'] = modules
    experiment = Experiment(shape, base_shape_config, neat_config)
    pop = experiment.run(**experiment_config)
    genome = pop.statistics.best_genome()
    return genome.fitness

def parallel_batch(neat_config, modules, n, c):
    pool = Pool(c)
    # Run each letters n times.
    params = sum((list(repeat((s, neat_config, modules), n)) for s in shapes), [])
    result = numpy.array(pool.map(process_wrapper, params))
    result.resize((len(shapes), n))
    pool.close()
    pool.join()
    return result

if __name__ == '__main__':
    neat_config = NeatConfig('experiments/config.txt')
    neat_config.report = False

    experiment_config = {
        'generations': 100,
        'cores': 1,
        'pop_size': 100
    }
    n = 10
    c = 12

    signal_config = {'prob_add': .0, 'prob_remove': .0, 'min_genes': 0,
                     'start_genes': 3, 'max_genes': 6 }
    module_params = [
        [(neighbors_distinct.NeighborModule, {})],
        [(divide_distinct.DivideDistinctModule, {})],
        # [(signal_0.Signal0Module, signal_config),
        #  (signal_1.Signal1Module, signal_config),
        #  (signal_2.Signal2Module, signal_config),
        #  (signal_3.Signal3Module, signal_config),
        #  (signal_4.Signal4Module, signal_config),
        #  (morphogen.MorphogenModule, signal_config)]
    ]

    neat_params = {
        'initial_connection': ['fully_connected'],#['fully_connected', 'partial 0.75', 'partial 0.5', 'partial 0.25', 'unconnected'],
        # 'initial_connection': ['unconnected', 'partial .25', 'partial .5',
        #                      'partial .75',  'fs_neat', 'fully_connected'],
        # 'initial_connection': ['fully_connected', 'unconnected', 'fs_neat'],
        # 'hidden_nodes': [0],#range(0, 17, 4),
        'compatibility_threshold': [2],#[.5, 1, 2, 4],#[1.2]#[.6, .8, 1, 1.2],#[.1, .2, .3, .4, .5]
        'max_stagnation': [10],
        # 'elitism': [1, 2, 4, 8, 16],
        # 'survival_threshold': [.05, .1, .2, .4]
        # 'max_stagnation': [5, 10, 15]
    }

    neat_iterator = list(enumerate(itertools.product(*neat_params.values())))
    module_iterator = list(enumerate(itertools.product(*module_params)))

    N = len(neat_iterator) * len(module_iterator)
    print "N = %i" % N

    for i, neat_param in neat_iterator:
        for j, modules in module_iterator:
            print '#' * 80
            print neat_param, list(modules)
            if i % 10 == 0 or N < 10:
                print i, '/', N

            for attr, param in zip(neat_params.keys(), neat_param):
                setattr(neat_config, attr, param)

            F = parallel_batch(neat_config, modules, n=n, c=c)

            # print params
            print str(F.mean())+'\t'+str(F.std())
            # print F
            print '\t'.join(shape_names)
            print '\t'.join(map(str, list(F.mean(axis=1))+list(F.std(axis=1))))
            print '#' * 80
            print
    # print genome_config['modules']
    # print experiment_config
