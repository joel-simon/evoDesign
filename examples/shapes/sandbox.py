""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from src.cellGenome import CellGenome
from src.views.viewer import Viewer
from examples.shapes.shapes import *
from itertools import product

genome_config = {
    'modules': [
    ],
    'inputs':[],
    'outputs':[('apoptosis', 'sigmoid')]
}

LOCAL_DIR = os.path.dirname(__file__)
CONFIG = Config(os.path.join(LOCAL_DIR, 'config.txt'))
CONFIG.genome_config = genome_config
DUMMY_GENOME = CellGenome.create_unconnected(1, CONFIG)

class Sandbox(PlanesShape):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        super(Sandbox, self).__init__(DUMMY_GENOME, bounds=(10, 10, 10), start=[])
        X, Y, Z = self.bounds

        self._create_target()

    def _create_target(self):
        X, Y, Z = self.bounds
        for x, y, z in product(range(X), range(Y), range(Z)):
            if self.target[x][y][z]:
                self.create_cell(x, y, z)

    def create_input(self, cell):
        return []

    def handle_all_outputs(self, outputs):
        pass

viewer = Viewer(bounds=(8,8,8))
simulation = Sandbox()
simulation.max_steps = 1
simulation.verbose = True
simulation.run(viewer=viewer)


