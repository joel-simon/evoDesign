from datetime import datetime

from src.experiment import Experiment
from src.modules import neighbors_distinct, divide_distinct, truss
from src.modules.signals import signal_0

from examples.table.table import Table
# from src.map_utils import empty

def is_static(x, y, z, X, Y, Z):
    return y == 0

def get_load(x, y, z, X, Y, Z):
    return [0, 0, 0]

if __name__ == '__main__':
    neat_config = './examples/table/config.txt'
    out_path = "./out/table_{:%B_%d_%Y_%H-%M}".format(datetime.now())

    modules = [ (neighbors_distinct.NeighborModule, {}),
                (divide_distinct.DivideDistinctModule, {}),
                # (truss.TrussModule, {'is_static': is_static,
                #                      'get_load': get_load,
                #                      'cell_width': .05,
                #                      }),
              ]

    start = [(0,0,0)]
    train_params = [{'bounds': (8, 8, 8), 'start':start}]

    experiment = Experiment(Table, neat_config, modules, train_params)
    experiment.run(cores=2, generations=200, pop_size=200)
    experiment.report(out_path)
