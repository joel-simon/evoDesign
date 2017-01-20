# import numpy as np
from src.modules import Module, BaseModuleSimulation

from src.map_utils import directions, shape

class DivideDistinctSimulation(BaseModuleSimulation):
    """docstring for DivideDistinctSimulation"""

    def __init__(self, simulation, module):
        super(DivideDistinctSimulation, self).__init__(simulation, module,
                                                               num_inputs=0,
                                                               num_outputs=6)

    def handle_output(self, x, y, z, outputs, current, next):
        X, Y, Z = current.shape
        if outputs[0] > .5 and x > 0 and not current[x-1, y, z]:
            self.simulation.create_cell(x-1, y, z)
            # next[x-1, y, z] = 1

        if outputs[1] > .5 and x < X-1 and not current[x+1, y, z]:
            self.simulation.create_cell(x+1, y, z)
            # next[x+1, y, z] = 1

        if outputs[2] > .5 and y > 0 and not current[x, y-1, z]:
            self.simulation.create_cell(x, y-1, z)
            # next[x, y-1, z] = 1

        if outputs[3] > .5 and y < Y-1 and not current[x, y+1, z]:
            self.simulation.create_cell(x, y+1, z)
            # next[x, y+1, z] = 1

        if outputs[4] > .5 and z > 0 and not current[x, y, z-1]:
            self.simulation.create_cell(x, y, z-1)
            # next[x, y, z-1] = 1

        if outputs[5] > .5 and z < Z-1 and not current[x, y, z+1]:
            self.simulation.create_cell(x, y, z+1)
            # next[x, y, z+1] = 1

class DivideDistinctModule(Module):
    """docstring for DivideDistinctModule"""
    name = 'divide'
    def __init__(self):
        super(DivideDistinctModule, self).__init__(gene=None,
                                            simulation=DivideDistinctSimulation)

        self.outputs = [('divide_%i'%i, 'sigmoid') for i in range(len(directions))]
