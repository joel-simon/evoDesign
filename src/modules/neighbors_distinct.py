import numpy as np
from src.modules import Module, BaseModuleSimulation
from src.map_utils import directions, shape

class NeighborSimulation(BaseModuleSimulation):
    """docstring for NeighborSimulation"""
    def __init__(self, simulation, module):
        super(NeighborSimulation, self).__init__(simulation, module, has_render=False)

    def create_input(self, cell):
        """ Binary encoding of six neighbors.
        """
        inputs = [0] * 6
        hmap = self.simulation.hmap
        x, y, z = cell.position
        X, Y, Z = shape(hmap)

        if x > 0 and hmap[x-1][y][z]:
            inputs[0] = 1

        if x < X-1 and hmap[x+1][y][z]:
            inputs[1] = 1

        if y > 0 and hmap[x][y-1][z]:
            inputs[2] = 1

        if y < Y-1 and hmap[x][y+1][z]:
            inputs[3] = 1

        if z > 0 and hmap[x][y][z-1]:
            inputs[4] = 1

        if z < Z-1 and hmap[x][y][z+1]:
            inputs[5] = 1

        return inputs

class NeighborModule(Module):
    """docstring for NeighborModule"""
    def __init__(self):
        super(NeighborModule, self).__init__(gene=None,
                                            simulation=NeighborSimulation)

        self.inputs = [('neighbor_%i'%i) for i in range(len(directions))]
