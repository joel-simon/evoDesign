from __future__ import print_function, division
import math
from datetime import datetime
# from compiler.ast import flatten
from itertools import product
from src.simulation import Simulation
from src.modules import neighbors_distinct, divide_distinct
from src.map_utils import shape, connected_mask, empty
from src.classification import balanced_accuracy_score

import numpy as np

class Shape(Simulation):
    """docstring for Shape"""
    inputs = []
    outputs = [('apoptosis', 'sigmoid')]
    def __init__(self, genome, bounds, start=[(0,0,0)]):
        super(Shape, self).__init__(genome, bounds, 32, start)
        # Target to be scored against.
        # self.target = self.create_target()
        self.target = None

    def cell_init(self, cell):
        # pass
        cell.userData['connected'] = True

    def create_input(self, cell):
        # x, y, z = cell.position
        # x_gradient = -1.0 + 2.0 * x / (self.bounds[0]-1)
        # y_gradient = -1.0 + 2.0 * y / (self.bounds[1]-1)
        # z_gradient = -1.0 + 2.0 * z / (self.bounds[2]-1)
        # return [x_gradient, y_gradient, z_gradient]
        return []

    def handle_output(self, cell, outputs):
        if outputs[0] > .5:
            self.destroy_cell(cell)

    def fitness(self):
        # print(self.cmap.sum())
        # return self.cmap.sum() / self.cmap.size
        # print(sum(self.cmap.flatten().tolist()))

        f = balanced_accuracy_score(self.target.flatten().tolist(), self.cmap.flatten().tolist())
        # print(self.cmap.sum(), self.target.sum(), f)
        return f

class PlanesShape(Shape):
    """docstring for CageShape"""
    def __init__(self, *args, **kwargs):
        super(PlanesShape, self).__init__(*args, **kwargs)
        target = empty(kwargs['bounds'])
        X, Y, Z = kwargs['bounds']
        target = np.zeros(shape=kwargs['bounds'], dtype=int)
        for x, y, z in product(range(0, X, 4), range(0, Y, 4), range(0, Z, 4)):
            target[x:x+2, y:y+2, z:z+2] = 1
        self.target = target#.tolist()

class CageShape(Shape):
    """docstring for CageShape"""
    def __init__(self, *args, **kwargs):
        super(CageShape, self).__init__(*args, **kwargs)
        target = empty(kwargs['bounds'])
        X, Y, Z = kwargs['bounds']
        target = np.ones(shape=kwargs['bounds'], dtype=int)
        target[2:-2, :, 2:-2] = 0
        target[:, 2:-2, 2:-2] = 0
        target[2:-2, 2:-2, :] = 0
        self.target = target#.tolist()
