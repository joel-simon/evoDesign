import numpy as np
from datetime import datetime

from src.experiment import Experiment
from src.modules import neighbors_distinct, divide_distinct
from src.modules.signals import signal_0

from examples.plant.plant import Plant

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
    neat_config = './examples/plant/config.txt'

    out_path = "./out/plant_{:%B_%d_%Y_%H-%M}".format(datetime.now())


    modules = [ (neighbors_distinct.NeighborModule, {}),
                (divide_distinct.DivideDistinctModule, {}),
                (signal_0.Signal0Module, {'start_genes':3, 'prob_add':0, 'prob_remove':3})
              ]

    params  = [{'bounds': (5, 12, 5), 'dirt_height': 3, 'steps': 50, 'start':[(2,2,2)]}]
    experiment = Experiment(Plant, neat_config, modules, params)
    experiment.run(cores=12, generations=100, pop_size=200)
    experiment.report(out_path)
