""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from neat import ctrnn, nn

from src.cellGenome import CellGenome
from src.views.viewer import Viewer

from src.modules import neighbors_distinct, divide_distinct, truss

from examples.table import Simulation

genome_config = {
    'modules': [
#     (MorphogenModule, {'start_genes': 1, 'min_genes': 0})
    # (Signal3Module, {'prob_add': .0, 'prob_remove': .0,
    #                  'min_genes': 0, 'start_genes': 3, 'max_genes': 6 }),

    # (neighbors_continuous.NeighborModule, {}),
    # (divide_theta.DivideThetaModule, {}),
        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {}),
        (truss.TrussModule, {'static_map': None})
    ],
    'inputs': [],
    'outputs': []
}

LOCAL_DIR = os.path.dirname(__file__)
CONFIG = Config(os.path.join(LOCAL_DIR, 'examples/config.txt'))
CONFIG.genome_config = genome_config
DUMMY_GENOME = CellGenome.create_unconnected(1, CONFIG)
network = nn.create_recurrent_phenotype(DUMMY_GENOME)

class Sandbox(Simulation):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        super(Sandbox, self).__init__(DUMMY_GENOME)

        self.destroy_cell(self.cells[0])

        for x in range(self.bounds[0]):
            for y in range(self.bounds[1]):
                for z in range(self.bounds[2]):
                    self.create_cell(x, y, z)

        # self.create_cell(2, 0, 2)
        # self.create_cell(2, 1, 2)
        # self.create_cell(2, 2, 2)
        # self.create_cell(2, 3, 2)
        # self.create_cell(2, 4, 2)


        # self.create_cell(0, 1, 0)
        # self.destroy_cell(self.cells[1])
        # for joint in self.cells[0].userData['body'].joints:
        #     print joint, joint in self.module_simulations[2].truss.joints
        # self.create_cell(0, 1, 0)

        # self.create_cell(0, 2, 0)
        # self.create_cell(0, 3, 0)
        # self.create_cell(0, 4, 0)

        # self.create_cell(0, 4, 1)
        # self.create_cell(0, 4, 2)
        # self.create_cell(0, 4, 3)
        # self.create_cell(0, 4, 4)
        

    def create_input(self, cell):
        return []

    def handle_output(self, cell, outputs):
        pass

    def create_beam(self):
        for i in [self.bounds[0]-1, 0]:
            for j in range(self.bounds[1]):
                if not self.hmap[i][j]:
                    self.create_cell((i, j))


        for i in range(self.bounds[0]):
            for j in [4, 8, self.bounds[1]-1]:
                if not self.hmap[i][j]:
                    self.create_cell((i, j))

    def step(self):
        # if self.step_count > 0 and self.step_count < self.bounds[1]:
        #     self.create_cell((5, self.step_count))
        #     self.destroy_cell(self.hmap[1][2])
        # super(Sandbox, self).step()
        # if self.step_count == 1:
        #     self.create_cell(1,1,1)
        # self.viewer.set_mesh(self.hmap)
        # self.viewer.main_loop()
        pass


    # def create_inputs(self, cell):
    #     # return []
    #     inputs = super(Sandbox, self).create_inputs(cell)
    #     print inputs
    #     return inputs

    # def handle_outputs(self, cell, outputs):
        # print(cell.position, outputs)
        # pass

    # def get_outputs(self):
    #     return []

    # def fitness(self):
    #     return 0

viewer = Viewer(bounds= (8,8,8))
simulation = Sandbox()
simulation.max_steps = 20
simulation.verbose = True
simulation.run(viewer=viewer)

