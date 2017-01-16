""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from src.cellGenome import CellGenome
from src.views.viewer import Viewer
from src.modules import truss
# from examples.beam.beam import Beam

from examples.table.table import Table
from examples.table.main import is_static, get_load

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

class Sandbox(Table):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        super(Sandbox, self).__init__(DUMMY_GENOME, bounds=(12, 12, 12), start=[])
        X, Y, Z = self.bounds

        for y in range(Y-1):
            self.create_cell(0, y, 0)
            self.create_cell(X-1, y, 0)
            self.create_cell(0, y, Z-1)
            self.create_cell(X-1, y, Z-1)

        for x in range(X):
            for z in range(Z):
                self.create_cell(x, Y-1, z)
                # self.create_cell(x, Y-1, z)
                # self.create_cell(x, Y-2, z)
                # self.create_cell(x, Y-3, z)
            # self.cells[-1].userData['body'].set_thickness(.079)

    def create_input(self, cell):
        return []

    def handle_all_outputs(self, outputs):
        pass

viewer = Viewer(bounds=(8,8,8))
simulation = Sandbox()
simulation.max_steps = 1
simulation.verbose = True
simulation.run(viewer=viewer)

# viewer.hold()

