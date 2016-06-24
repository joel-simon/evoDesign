import os
import math

from neat.config import Config

from src.cellGenome import CellGenome
from src.simulation import Simulation

from src.physics.softPhysics import SoftPhysics

local_dir = os.path.dirname(__file__)
config  = Config(os.path.join(local_dir, 'config.txt'))
dummy_genome = CellGenome.create_unconnected(1, config)

# physics = VisualVoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
#                                       damping=0.3, timestep = .02, maxsteps=999)

class Sandbox(Simulation):
  """Extend the simualtion to inject arbitrary cell behavior."""
  def step(self):
    # print(self.steps)
    if self.steps == 1:
      self.divide_cell(self.cells[0])
    # if self.steps == 2:
    #   self.divide_cell(self.cells[0])
    self.physics.run()

physics = SoftPhysics(verbose=True, max_steps=100)
# physics.renderer = None
sim = Sandbox(dummy_genome, physics, max_steps=None, verbose=True)


r = 30
cell = sim.create_cell(position=(0, r), size=[r])
# cell = sim.create_cell(position=(0, 5*r+10), size=[r])
# cell = sim.create_cell(position=(1.5*r, 3*r+10), size=[r])
# cell = sim.create_cell(position=(-r, 3*r+10), size=[r])
sim.run()
print('Sandbox Comlete.')
