""" A testing and experimentation enviornment.
"""
import os

from neat.config import Config
from neat import ctrnn, nn

from src.cellGenome import CellGenome
from src.hexmap import Map
from src.hexSimulation import HexSimulation
from src.views import View
from src.modules.physics import PhysicsModule

from experiments.tree import Simulation, genome_config

# bounds = (8, 12)
# static_map = Map(bounds)
# for col in range(bounds[1]):
#     static_map[0][col] = 1

LOCAL_DIR = os.path.dirname(__file__)
CONFIG = Config(os.path.join(LOCAL_DIR, 'config.txt'))
# CONFIG.node_gene_type = ctrnn.CTNodeGene
CONFIG.genome_config = genome_config
# CONFIG.genome_config = {
#     'inputs': [],
#     'outputs':[],
#     'modules' : [
#         (PhysicsModule, {'static_map': static_map})
#     ],
# }
DUMMY_GENOME = CellGenome.create_unconnected(1, CONFIG)
network = nn.create_recurrent_phenotype(DUMMY_GENOME)
# print(network)
# print(network.activate([0]*8))

class Sandbox(Simulation):
    """ Extend the simualtion to inject arbitrary cell behavior. """
    def __init__(self):
        super(Sandbox, self).__init__(DUMMY_GENOME)
        # super(Sandbox, self).__init__(DUMMY_GENOME, max_steps=10, bounds=bounds)
        for i in range(self.bounds[0]):
            for j in range(self.bounds[1]):
        #         d = self.hmap.distance((i,j), (4,4))
        #         if d == 3 or d == 4:
                if not self.hmap[i][j]:
                    self.create_cell((i, j))

        # self._calculate_light()
        # self.filter_unconnected()

        # stem_col= 0
        # for i in range(1, 12):#self.bounds[0]-1):
        #     if not self.hmap[i][stem_col]:
        #         self.create_cell((i, stem_col))


        # for j in range(self.bounds[1]):
        #     if not self.hmap[8][j]:
        #         self.create_cell((8, j))


    # def step(self):
        # if self.step_count == 2:
        #     self.destroy_cell(self.hmap[1][2])
        # super(Sandbox, self).step()
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
simulation.verbose = True

view = View(600, 800, simulation)
simulation.run(view)
view.hold()
