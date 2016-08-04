import os, math, random
from neat.config import Config
from neat import ctrnn
from src.cellGenome import CellGenome

from src.hexSimulation import HexSimulation
from src.hexRenderer import HexRenderer as Renderer

from experiments.shapes import Shapes

local_dir = os.path.dirname(__file__)
config  = Config(os.path.join(local_dir, 'config.txt'))
config.node_gene_type = ctrnn.CTNodeGene
config.genome_config = {
    'inputs': ['derp'],
    'outputs':['foo'],
    'num_morphogens': 1,
    'morphogen_thresholds': 4
}
dummy_genome = CellGenome.create_unconnected(1, config)

class Sandbox(HexSimulation):
    # """Extend the simualtion to inject arbitrary cell behavior."""
    def __init__(self, *args, **kwargs):
        super(Sandbox, self).__init__(dummy_genome)

        # for i in range(self.bounds[0]):
        #     for j in range(self.bounds[1]):
        #         d = self.hmap.distance((i,j), (4,4))
        #         if d == 3 or d == 4:
        #             self.create_cell((i, j))

        # self._calculate_light()

        # self.filter_unconnected()
        self.create_cell((0,0))
        # for coords in list(self.hmap.neighbor_coords((4,4)))[:2]:
        #     self.create_cell(coords)

    def create_target(self):
        return []

    def create_inputs(self, cell):
        return [0]

    def handle_outputs(self, cell, outputs):
        self.divide_cell(cell, 5)
        pass

    def get_outputs(self):
        return [0,0,-1.0]

    def fitness(self):
        return 0
        # for coords in self.hmap.neighbor_coords((4,4)):
        #     print(coords)
        #     self.create_cell(coords)

        # self.create_cell((4,4))
        # self.create_cell((1,4))
        # self.create_cell((1,5))
        # self.create_cell((1,5))
        # for i in range(7):
        #
        #     self.create_cell((i,1))

        # for i in range(2,7):
        #     self.create_cell((7,i))

        # for i in range(8):
        #     for j in range(8):
        #         self.create_cell((i,j))

    # def Step(self, *args):
    #     super(Sandbox, self).Step(*args)

        # if self.stepCount%2 == 0:
        # pygame.image.save(self.screen, './out_temp/' + str(self.stepCount)+'.jpg')
        # print('saved')

renderer = Renderer()
# simulation = Sandbox()
simulation = Sandbox(max_steps=2, verbose=False, bounds=(8,8))
simulation.verbose = True
simulation.run(renderer)
renderer.hold()
