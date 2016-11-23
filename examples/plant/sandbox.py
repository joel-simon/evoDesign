""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from src.cellGenome import CellGenome
from src.views.viewer import Viewer
from src.modules import truss

from examples.plant.plant import Plant
from itertools import product

genome_config = {
    'modules': [
        # (truss.TrussModule, {
        #     'is_static': is_static,
        #     'get_load': get_load,
        #     'cell_width': .02})
    ],
    'inputs':[],
    'outputs':[('apoptosis', 'sigmoid')]
}

LOCAL_DIR = os.path.dirname(__file__)
CONFIG = Config(os.path.join(LOCAL_DIR, 'config.txt'))
CONFIG.genome_config = genome_config
DUMMY_GENOME = CellGenome.create_unconnected(1, CONFIG)

class Sandbox(Plant):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        cell_width = 1.0/20

        super(Sandbox, self).__init__(DUMMY_GENOME, dirt_height = 4,
                                bounds=(7, 16, 7), start=[(3,3,3),(3,4,3)])
        X, Y, Z = self.bounds

        # stalk
        for y in range(Y-1):
            self.create_cell(0, y, 0)

        # leaves
        for x, z in product(range(X), range(Z)):
            self.create_cell(x, Y-1, z)

        # roots
        for z in range(1, Z):
            self.create_cell(0, 0, z)
            self.create_cell(0, 2, z)


        for x, z in product(range(1,X), range(0, Z, 2)):
            self.create_cell(x, 0, z)
            self.create_cell(x, 2, z)


    def create_input(self, cell):
        return []

    def handle_all_outputs(self, outputs):
        pass

viewer = Viewer(bounds=(8,8,8))
simulation = Sandbox()
simulation.max_steps = 1
simulation.verbose = True
simulation.run(viewer=viewer)

