import numpy as np
from datetime import datetime

from src.experiment import Experiment
from src.modules import neighbors_distinct, divide_distinct
from src.modules.signals import signal_0

from examples.bookcase.bookcase import Bookcase

# def get_items(a, mean_height, height_std, height_min=2, height_max=5):
#     items = []
#     depth = 2
#     n_items = int(a/float(mean_height) * 1.25)
#     heights = np.random.normal(mean_height, height_std, [n_items]).astype(int)
#     heights[heights < height_min] = height_min
#     heights[heights > height_max] = height_max
#     items = [(h, depth) for h in heights]
#     return items

if __name__ == '__main__':
    neat_config = './examples/bookcase/config.txt'

    out_path = "./out/bookcase_{:%B_%d_%Y_%H-%M}".format(datetime.now())
    # out_path = "./out/bookcase_single_nogradient".format(datetime.now())
    # out_path = "./out/bookcase_single_gradient".format(datetime.now())

    items = [(3, 2), (5, 3), (5, 3), (4, 2), (4, 2), (3, 2), (4, 2), (5, 4),\
           (5, 3), (4, 2), (3, 2), (4, 3), (4, 2), (4, 2), (4, 3),\
           (4, 2), (4, 2), (5, 3), (5, 3), (4, 2), (3, 2), (4, 3), (4, 2),\
           (4, 2), (3, 2), (4, 2), (4, 3)]

    modules = [ (neighbors_distinct.NeighborModule, {}),
                (divide_distinct.DivideDistinctModule, {}),
                # (signal_0.Signal0Module, {})
              ]

    # params = [{'bounds': (4, 16, 4), 'items':get_items(4*16, 3, 1)},
    #           {'bounds': (16, 4, 4), 'items':get_items(16*4, 3, 1)},

    #           {'bounds': (12, 8, 4), 'items':get_items(12*8, 3, 1)},
    #           {'bounds': (8, 12, 4), 'items':get_items(8*12, 3, 1)},
    #          ]
    params  = [{'bounds': (8, 29, 6), 'items': items}]
    experiment = Experiment(Bookcase, neat_config, modules, params)
    experiment.run(cores=12, generations=200, pop_size=200)
    experiment.report(out_path)
