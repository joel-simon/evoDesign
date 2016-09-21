""" A testing and experimentation enviornment.
"""
import os

from src.neat_custom.config import Config
from neat import ctrnn, nn

from src.cellGenome import CellGenome
from src.hexmap import Map
from src.hexSimulation import HexSimulation
from src.views import View

# from experiments.tree import Simulation, genome_config
# from experiments.shapes import genome_config, R as Simulation
from experiments.table import Simulation, genome_config

from src.modules.morphogen import MorphogenModule
import time
# genome_config['modules'] = [
#     (MorphogenModule, {'start_genes': 1, 'min_genes': 0})
    # (Signal3Module, {'prob_add': .0, 'prob_remove': .0,
    #                  'min_genes': 0, 'start_genes': 3, 'max_genes': 6 }),

    # (neighbors_continuous.NeighborModule, {}),
    # (divide_theta.DivideThetaModule, {}),

    # (neighbors_distinct.NeighborModule, {}),
    # (divide_distinct.DivideDistinctModule, {})
# ]


LOCAL_DIR = os.path.dirname(__file__)
CONFIG = Config(os.path.join(LOCAL_DIR, 'experiments/shape_config.txt'))
CONFIG.genome_config = genome_config
DUMMY_GENOME = CellGenome.create_unconnected(1, CONFIG)
network = nn.create_recurrent_phenotype(DUMMY_GENOME)

class Sandbox(Simulation):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        super(Sandbox, self).__init__(DUMMY_GENOME)

        for row in range(1, self.bounds[0]):
            self.create_cell((row, 0))

        for row in range(self.bounds[0]-1):
            self.create_cell((row, 1))

        for col in range(1, self.bounds[1]):
            self.create_cell((5, col))
        # for row in range(0, 4):
        #     for col in range(2, self.bounds[1]-2):
        #         self.destroy_cell(self.hmap[row][col])
        #
        #     self.create_cell((5, col))
        # self._calculate_light()
        # self.filter_unconnected()

        # self.create_cell((0, 0))
        # self.create_cell((0, 1))
        # self.create_cell((4, 0))
        # self.create_cell((4, 1))
        # self.create_cell((5, 1))
        # self.create_cell((5, 2))
        # self.create_cell((4, 2))
        # self.create_cell((3, 1))

        # self.destroy_cell(self.hmap[4][1])
        # self.create_cell((4,1))

        # self.create_cell((1, 6))

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
        super(Sandbox, self).step()
        time.sleep(1)
        # for cell in [c for c in self.cells]:
        #     for i in range(6):
        #         self.divide_cell(cell, i)
        # print(self.genome)

    # def create_inputs(self, cell):
    #     # return []
    #     inputs = super(Sandbox, self).create_inputs(cell)
    #     print inputs
    #     return inputs

    # def handle_outputs(self, cell, outputs):
        # print(cell.userData['coords'], outputs)
        # pass

    # def get_outputs(self):
    #     return []

    # def fitness(self):
    #     return 0


simulation = Sandbox()
simulation.max_steps = 2
simulation.verbose = True
view = View(600, 800, simulation)
simulation.run(view)
simulation.step()
view.hold()
