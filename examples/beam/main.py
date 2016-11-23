import numpy as np
from datetime import datetime

from src.experiment import Experiment
from src.modules import neighbors_distinct, divide_distinct, truss
from src.modules.signals import signal_0

from examples.beam.beam import Beam
from src.map_utils import empty

def is_static(x, y, z, X, Y, Z):
    return x == 0

def get_load(x, y, z, X, Y, Z):
    # if (y == Y-1) and (x == X-1):
    #     return [0, -200000, 0]
    # else:
    return [0, 0, 0]


if __name__ == '__main__':
    neat_config = './examples/beam/config.txt'
    out_path = "./out/beam_{:%B_%d_%Y_%H-%M}".format(datetime.now())

    modules = [ (neighbors_distinct.NeighborModule, {}),
                (divide_distinct.DivideDistinctModule, {}),
                (truss.TrussModule, {'is_static': is_static, 'get_load': get_load}),
                # (signal_0.Signal0Module, {})
              ]

    start = [(0,0,0)]
    train_params = [{'bounds': (7, 2, 1), 'start':start}]

    experiment = Experiment(Beam, neat_config, modules, train_params)
    experiment.run(cores=1, generations=25, pop_size=50)
    experiment.report(out_path)

    # from src.views.viewer import Viewer
    # viewer = Viewer(bounds=(8,8,8))
    # simulation = Beam()
    # simulation.max_steps = 20
    # simulation.verbose = True
    # simulation.run(viewer=viewer)

