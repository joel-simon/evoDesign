from collections import defaultdict
from cell import Cell
from Vector import Vector
from physics import VoronoiSpringPhysics
import random

import time

class Simulation(object):
  def __init__(self, genome, physics_framework, dimensions, starting_size=50):
    self.genome = genome
    self.cells = dict()
    self.next_cell_id = 0
    self.morph_decay = 0.9
    self.physics = physics_framework

    for i in range(starting_size):
      x = 400+20*(random.random()-.5)
      y = 50+20*(random.random()-.5)
      self.create_cell(p=Vector(x,y))

  def create_cell(self, p, cell_type=0):
    cell = Cell(self.next_cell_id, self.genome, p, cell_type)
    self.physics.add_node(cell)
    self.cells[cell.id] = cell
    self.next_cell_id += 1
    return cell

  # def cell_neighbors(self, cell):
  #   return self.physics.neighbors(cell)

  def spread_morphogens(self):
    pass
    # next_morphogens = defaultdict(lambda : [0] * self.genome.morphogens)

    # for cell1 in self.cells.values():
    #   neighbors = self.cell_neighbors(cell1)
    #   for cell2 in neighbors:
    #     for m in range(self.genome.morphogens):
    #       morph = (cell1.mophogens[m] / len(neighbors)) * self.morph_decay
    #       next_morphogens[cell2.id][m] += morph

    # for cell in self.cells.values():
    #   cell.mophogens = next_morphogens[cell.id]

  def calculate_light(self):
    pass
    # dx = 10
    # # dy = 10
    # foo = [[]] * dx
    # for cell_id, cell in self.cells.items()
    #   i = int(cell.node.p[0]/800)
    #   foo[i].append((cell_id, cell.))

  def step(self):
    # self.spread_morphogens()
    # self.calculate_light()

    outputs = [(cell, cell.activate()) for cell in self.cells.values()]

    for cell, cell_out in outputs:
      # Apoptopis
      if cell_out['apoptosis']:
        self.physics.remove_node(cell)
        del self.cells[cell.id]

      # Cell division
      if cell_out['growth'] != None:
        r = 5
        dd = Vector(*cell_out['growth_direction']) * r
        daughter = self.create_cell(dd + cell.node.p.copy(), cell.cell_type)

        # for i, m in enumerate(cell.morphogens):
        #   daughter.morphogens[i] += m/2
        #   cell.morphogens[i] /= 2

      # Emit Morphogens
      for i, m in enumerate(cell_out['morphogens']):
        cell.morphogens[i] += m

    physics.run()


  def finished(self):
    if len(self.cells) == 0:
      return True

    if len(self.cells) > 50:
      return True

    return False

  def run(self, generations):
    print('Running %i generations' % generations)
    steps = 0
    while steps < generations and not self.finished():
      self.step()
      steps += 1

    print('done')


# Simulate a random genomes
if __name__ == '__main__':
  import os
  from neat import nn, parallel, population, visualize
  from neat.config import Config
  from cellGenome import CellGenome
  from cell import DummyCell
  from visualize import VisualVoronoiSpringPhysics
  import pygame, sys

  local_dir = os.path.dirname(__file__)
  config  = Config(os.path.join(local_dir, 'config.txt'))
  dummy_genome = CellGenome.create_unconnected(1, config)

  # physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=400.0, damping=0.5, timestep = .2)

  physics = VisualVoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                        damping=0.5, timestep = .05)

  sim = Simulation(dummy_genome, physics, (800, 800))
  sim.run(10)
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

