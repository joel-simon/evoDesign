# Simulate a random genomes
import os
from neat import nn, parallel, population, visualize
from neat.config import Config
from cellGenome import CellGenome
from visualize import VisualVoronoiSpringPhysics
from simulation import Simulation
import pygame, sys
import random
from Vector import Vector

local_dir = os.path.dirname(__file__)
config  = Config(os.path.join(local_dir, 'config.txt'))
dummy_genome = CellGenome.create_unconnected(1, config)

physics = VisualVoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                      damping=0.3, timestep = .05)

sim = Simulation(dummy_genome, physics, (800, 800))

for i in range(190):
  x = 400+20*(random.random()-.5)
  y = 400+20*(random.random()-.5)
  sim.create_cell(p=Vector(x,y))

sim.run(1)
list(sim.cells.values())[0].morphogen_productions[0][0] = .1
# cell = list(sim.cells.values())[1].morphogen_productions[0][0] = .1
# sim.spread_morphogen()


for i in range(10):
  x = 400+20*(random.random()-.5)
  y = 400+20*(random.random()-.5)
  sim.create_cell(p=Vector(x,y))
  # sim.spread_morphogen(steps=1000)
  sim.step()


# for cell in sim.cells.values():
#   print(cell.morphogen_concentrations)
while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()

