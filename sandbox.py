import os, math, random
from neat.config import Config
from src.cellGenome import CellGenome

# from src.simulation2 import Simulation
from src.hexSimulation import HexSimulation
from src.hexVisualize import HexRenderer as Renderer
# import pygame

local_dir = os.path.dirname(__file__)
config  = Config(os.path.join(local_dir, 'config.txt'))
config.genome_config = {
    'inputs': ['derp'],
    'outputs':['foo'],
    'num_morphogens': 1,
    'morphogen_thresholds': 4
}
dummy_genome = CellGenome.create_unconnected(1, config)

class Sandbox(HexSimulation):
    """Extend the simualtion to inject arbitrary cell behavior."""
    # def __init__(self, *args, **kwargs):
    #     super(Sandbox, self).__init__(*args, **kwargs)
        # self.renderer._viewZoom = .2
    def create_inputs(self, cell):
        return [0]

    def handle_outputs(self, cell, outputs):
        pass

    def set_up(self):

        # for coords in self.hmap.neighbor_coords((4,4)):
        #     print(coords)
        #     self.create_cell(coords)

        # self.create_cell((4,4))
        # self.create_cell((1,4))
        # self.create_cell((1,5))
        # self.create_cell((1,5))
        # for i in range(7):
        #     self.create_cell((i,0))
        #     self.create_cell((i,1))

        # for i in range(2,7):
        #     self.create_cell((7,i))

        for i in range(8):
            for j in range(8):
                self.create_cell((i,j))


        # self.create_cell((1,0))
    # def _get_outputs(self):
        # if self.stepCount == 100:
        #     return [{'divide': True} for cell in self.cells]
        # return [{'grow':1000} for cell in self.cells]
        # if self.stepCount < 40:
            # return [{'grow':1000} for cell in self.cells]

            # return [{'contract':True} for cell in self.cells]
        # else:
        #     return [{'grow':1000} for cell in self.cells]
        # print([cell.body.pressure for cell in self.cells])
        # return [{} for cell in self.cells]

    # def Step(self, *args):
    #     super(Sandbox, self).Step(*args)

        # if self.stepCount%2 == 0:
        # pygame.image.save(self.screen, './out_temp/' + str(self.stepCount)+'.jpg')
        # print('saved')

renderer = Renderer()
simulation = Sandbox(dummy_genome, max_steps=200, verbose=False, bounds=(8,8))
simulation.verbose = True
simulation.set_up()
simulation.run(renderer)
renderer.hold()

# cell = sim.create_cell(position=(0,0))
# sim.cells.append(cell)

# sim.cells.append()
# sim.cells.append(sim.create_cell((0,1)))
# sim.cells.append(sim.create_cell((1,1)))
# sim.cells.append(sim.create_cell((7,1)))
# sim.cells.append(sim.create_cell((7,2)))
# sim.cells.append(sim.create_cell((7,3)))
# for i in range(50):
#     for j in range(50):
#         sim.cells.append(sim.create_cell((i,j)))
#     # sim.cells.append(sim.create_cell((i,0)))


# for i in range(8):
#     sim.cells.append(sim.create_cell((i,0)))

print('VALID')
sim.run()
