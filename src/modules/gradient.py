from __future__ import division
from src.modules import Module, BaseModuleSimulation
import numpy as np

class GradientSimulation(BaseModuleSimulation):
    """docstring for GradientSimulation"""

    def __init__(self, simulation, module):
        super(GradientSimulation, self).__init__(
            simulation,
            module,
            num_inputs=3,
            num_outputs=0
        )

    def cell_init(self, x, y, z):
        pass

    def cell_destroy(self, x, y, z):
        pass

    def create_input(self, x, y, z, input, cmap):
        input[0] = -1.0 + 2.0 * x / self.simulation.max_steps
        input[1] = -1.0 + 2.0 * y / self.simulation.max_steps
        input[2] = -1.0 + 2.0 * y / self.simulation.max_steps

    def handle_output(self, x, y, z, outputs, current, next):
        pass

    def step(self):
        pass

class GradientModule(Module):
    """docstring for GradientModule"""
    name = 'gradient'
    def __init__(self):
        super(GradientModule, self).__init__(gene=None, simulation=GradientSimulation)

        self.inputs = ['gradient_x', 'gradient_y', 'gradient_z']
        self.outputs = []
