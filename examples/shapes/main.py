from datetime import datetime

from src.experiment import Experiment
from src.modules import neighbors_distinct, divide_distinct, age, gradient, morphogen

from examples.shapes.shapes import *

if __name__ == '__main__':
    neat_config = './examples/shapes/config.txt'
    out_path = "./out/Cage/{:%B_%d_%Y_%H-%M}".format(datetime.now())

    modules = [
        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {}),
        (age.AgeModule, {}),
        (morphogen.MorphogenModule, {'min_genes':1, 'max_genes':1})
    ]

    start = [(0,0,0)]
    train_params = [{'bounds': (8, 8, 8), 'start':start}]

    experiment = Experiment(CageShape, neat_config, modules, train_params)
    experiment.run(cores=1, generations=1, pop_size=10)
    experiment.report(out_path)
