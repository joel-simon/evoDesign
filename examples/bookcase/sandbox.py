""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from src.cellGenome import CellGenome
from src.views.viewer import Viewer
from src.modules import truss

from examples.bookcase.bookcase import Bookcase
# from examples.bookcase.main import get_items
from examples.bookcase.get_items import get_items
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

# items = [(3, 2), (2, 2), (2, 2), (4, 2), (2, 2), (2, 2), (2, 2), 
#         (3, 2), (3, 2), (2, 2), (3, 2), (3, 2), (3, 2), (3, 2),
#         (2, 2), (2, 2), (2, 2), (2, 2), (3, 2), (2, 2), (2, 2),
#         (2, 2), (2, 2), (3, 2), (3, 2), (2, 2)]

class Sandbox(Bookcase):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        cell_width = 1.0/20
        items = get_items(8*29 /2, cell_width)
        print items

        super(Sandbox, self).__init__(DUMMY_GENOME, items=items,\
                                        bounds=(8, 29, 6), start=[])
        X, Y, Z = self.bounds

        # Back piece
        # for x, y in product(range(X), range(Y)):
        #     self.create_cell(x, y, 0)

        # Sides
        for y, z in product(range(Y), range(Z)):
            self.create_cell(0, y, z)
            self.create_cell(X-1, y, z)

        # Floors
        for x, y, z in product(range(1,X-1), range(0,Y,7), range(Z)):
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

