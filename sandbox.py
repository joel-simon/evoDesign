import os, math, random
from neat.config import Config
from src.cellGenome import CellGenome

# from src.simulation2 import Simulation
from src.hexSimulation import Simulation

import pygame

local_dir = os.path.dirname(__file__)
config  = Config(os.path.join(local_dir, 'config.txt'))
config.genome_config = {
    'inputs': [],
    'outputs':[],
    'num_morphogens': 1,
    'morphogen_thresholds': 4
}
dummy_genome = CellGenome.create_unconnected(1, config)

class Sandbox(Simulation):
    """Extend the simualtion to inject arbitrary cell behavior."""
    # def __init__(self, *args, **kwargs):
    #     super(Sandbox, self).__init__(*args, **kwargs)
        # self.renderer._viewZoom = .2

    def _get_outputs(self):
        # if self.stepCount == 100:
        #     return [{'divide': True} for cell in self.cells]
        # return [{'grow':1000} for cell in self.cells]
        # if self.stepCount < 40:
            # return [{'grow':1000} for cell in self.cells]

            # return [{'contract':True} for cell in self.cells]
        # else:
        #     return [{'grow':1000} for cell in self.cells]
        # print([cell.body.pressure for cell in self.cells])
        return [{} for cell in self.cells]

    def Step(self, *args):
        super(Sandbox, self).Step(*args)
        # if self.stepCount%2 == 0:
        # pygame.image.save(self.screen, './out_temp/' + str(self.stepCount)+'.jpg')
        # print('saved')

sim = Sandbox(dummy_genome, max_steps=None, verbose=False, bounds=50)
# cell = sim.create_cell(position=(0,0))
# sim.cells.append(cell)

# sim.cells.append(sim.create_cell((0,0)))
# sim.cells.append(sim.create_cell((7,1)))
# sim.cells.append(sim.create_cell((7,2)))
# sim.cells.append(sim.create_cell((7,3)))
for i in range(20):
    sim.cells.append(sim.create_cell((i,1)))
    sim.cells.append(sim.create_cell((i,0)))

for i in range(2,20):
    sim.cells.append(sim.create_cell((19,i)))

# for i in range(8):
#     sim.cells.append(sim.create_cell((i,0)))

print('VALID')
sim.run()
