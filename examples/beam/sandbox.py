""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from src.cellGenome import CellGenome
from src.views.viewer import Viewer
from src.modules import truss
from examples.beam.beam import Beam

def is_static(x, y, z, X, Y, Z):
    return x == 0

def get_load(x, y, z, X, Y, Z):
    if (y == Y-1) and (x == X-1):
        return [0, -200000, 0]
    else:
        return [0, 0 , 0]

genome_config = {
    'modules': [
        (truss.TrussModule, {'is_static': is_static, 'get_load': get_load})
    ],
    'inputs':[],
    'outputs':[('apoptosis', 'sigmoid')]
}

LOCAL_DIR = os.path.dirname(__file__)
CONFIG = Config(os.path.join(LOCAL_DIR, 'beam_config.txt'))
CONFIG.genome_config = genome_config
DUMMY_GENOME = CellGenome.create_unconnected(1, CONFIG)

class Sandbox(Beam):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        super(Sandbox, self).__init__(DUMMY_GENOME, bounds=(4, 1, 1))

        X, Y, Z = self.bounds
        self.destroy_cell(self.cells[0])
        for x in range(X):
            for y in range(1):
                self.create_cell(x, y, 0)

                self.cells[-1].userData['body'].set_thickness(.079)


        self.cells[0].userData['body'].set_scale([1, .8, .8])
        self.cells[1].userData['body'].set_scale([1, .7, .7])
        self.cells[2].userData['body'].set_scale([1, .6, .6])
        self.cells[3].userData['body'].set_scale([1, .4, .4])
        # # print self.cells[0].userData['body'].joint_positions
        # for cell in self.cells:
        #     cell.userData['body'].set_scale(1)
        # cell.userData['body'].set_scale([1,2, 1])

        # self.cells[-1].userData['body'].set_scale([2,2,2])
        # self.cells[0].userData['body'].set_thickness(.06)
        # self.cells[2].userData['body'].set_scale([1.0, .5, 1.])

        # print self.cells[0].userData['body'].joint_positions

    def create_input(self, cell):
        return []

    def handle_all_outputs(self, outputs):
        pass

viewer = Viewer(bounds=(8,8,8))
simulation = Sandbox()
simulation.max_steps = 1
simulation.verbose = True
simulation.run(viewer=viewer)

