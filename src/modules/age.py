from __future__ import division
from src.modules import Module, BaseModuleSimulation
import numpy as np

class AgeSimulation(BaseModuleSimulation):
    """docstring for AgeSimulation"""

    def __init__(self, simulation, module):
        super(AgeSimulation, self).__init__(
            simulation,
            module,
            num_inputs=1,
            num_outputs=0
        )
        self.ages = np.zeros(simulation.bounds, dtype=int)

    def cell_init(self, x, y, z):
        self.ages[x, y, z] = 1

    def cell_destroy(self, x, y, z):
        self.ages[x, y, z] = 0

    def create_input(self, x, y, z, input, cmap):
        input[0] = -1.0 + 2.0 * self.ages[x, y, z] / self.simulation.max_steps

    def handle_output(self, x, y, z, outputs, current, next):
        pass

    def step(self):
        self.ages[self.ages > 0] += 1

class AgeModule(Module):
    """docstring for AgeModule"""
    name = 'age'
    def __init__(self):
        super(AgeModule, self).__init__(gene=None, simulation=AgeSimulation)

        self.inputs = ['age']
        self.outputs = []
