import os, math, random
from neat.config import Config
from src.cellGenome import CellGenome
from src.simulation2 import Simulation


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
    def _get_outputs(self):
        # if self.stepCount == 100:
        #     return [{'divide': True} for cell in self.cells]
        return [{'grow':.5} for cell in self.cells]

sim = Sandbox(dummy_genome, max_steps=None, verbose=False, bounds=None)
cell = sim.create_cell(position=(0, 6), bodies=40)
sim.cells.append(cell)

print('VALID')
sim.run()
