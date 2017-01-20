import numpy as np
from src.modules import Module, BaseModuleSimulation
from src.map_utils import directions, shape

class NeighborSimulation(BaseModuleSimulation):
    """docstring for NeighborSimulation"""
    def __init__(self, simulation, module):
        super(NeighborSimulation, self).__init__(simulation, module,
                                                                num_inputs=6,
                                                                num_outputs=0)

    def create_input(self, x, y, z, input, cmap):
        """ Binary encoding of six neighbors.
        """
        X, Y, Z = cmap.shape

        if x > 0 and cmap[x-1,y,z]:
            input[0] = 1

        if x < X-1 and cmap[x+1,y,z]:
            input[1] = 1

        if y > 0 and cmap[x,y-1,z]:
            input[2] = 1

        if y < Y-1 and cmap[x,y+1,z]:
            input[3] = 1

        if z > 0 and cmap[x,y,z-1]:
            input[4] = 1

        if z < Z-1 and cmap[x,y,z+1]:
            input[5] = 1

        # print(input)


class NeighborModule(Module):
    """docstring for NeighborModule"""
    name = 'neighbors'
    def __init__(self):
        super(NeighborModule, self).__init__(gene=None,
                                            simulation=NeighborSimulation)

        self.inputs = [('neighbor_%i'%i) for i in range(len(directions))]
