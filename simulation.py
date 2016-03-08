from collections import defaultdict
from cell import Cell
from Vector import Vector
from force_diagram import ForceDirected, Graph, Node, plot
import random

import time

# from scipy.spatial import Voronoi

# import pygame
# import pygame.gfxdraw
# pygame.init()
# screen = pygame.display.set_mode((800, 800))

class Simulation(object):
  def __init__(self, genome, dimensions, draw):
    self.genome = genome
    self.cells = dict()
    self.draw = draw
    # self.neighbors = set()
    self.next_cell_id = 0
    self.morph_decay = 0.9
    self.node_to_cell = dict()
    self.graph = Graph()
    self.FD = ForceDirected(self.graph, stiffness=400.0, repulsion=400.0, damping=0.5, timestep = .2)

    for i in range(5):
      self.add_cell(Vector(400+20*(random.random()-.5), 5+5*(random.random()-.5)), 0)

  def add_cell(self, p, cell_type):
    node = self.graph.add_node(p)
    cell = Cell(self.next_cell_id, self.genome, node, cell_type)
    self.cells[cell.id] = cell
    self.node_to_cell[node.id] = cell.id
    self.next_cell_id += 1
    return cell

  def cell_neighbors(self, cell):
    for node in self.graph.neighbors(cell.node):
      yield self.node_to_cell[node.id]

  # def spread_morphogens(self):
  #   next_morphogens = defaultdict(lambda : [0] * self.genome.morphogens)

  #   for cell1 in self.cells.values():
  #     neighbors = self.cell_neighbors(cell1)
  #     for cell2 in neighbors:
  #       for m in range(self.genome.morphogens):
  #         morph = (cell1.mophogens[m] / len(neighbors)) * self.morph_decay
  #         next_morphogens[cell2.id][m] += morph

  #   for cell in self.cells.values():
  #     cell.mophogens = next_morphogens[cell.id]

  def plot(self, graph):
    map_pos = lambda p: (int(p[0]), 800-int(p[1]))
    screen.fill((255,255,255))

    for cell in self.cells.values():
      x, y = map_pos(cell.node.p)
      # print(cell.morphogens)
      alpha = min(100 * cell.morphogens[0], 255)
      pygame.gfxdraw.filled_circle(screen, x, y, 4, (255,10,10, alpha))
      # pygame.gfxdraw.filled_circle(screen, x, y, 3, (10,10,10))

    for (node1, node2) in self.graph.edges():
      x1, y1 = map_pos(node1.p)
      x2, y2 = map_pos(node2.p)
      d = node1.p - node2.p #the direction of the spring
      d = Vector(d[0]*1.5, d[1])
      r = node1.r + node2.r
      if d.norm() < 2*r:
        pygame.gfxdraw.line(screen, x1, y1, x2, y2, (10,10,10))

    # vor = Voronoi([cell.node.p for cell in self.cells.values()])
    # verts = vor.vertices
    # for region in vor.regions:
    #   if len(region) > 2 and -1 not in region:
    #     pointlist = [map_pos(verts[i]) for i in region]
    #     pygame.gfxdraw.aapolygon(screen, pointlist ,(10,10,10))

    pygame.display.flip()
    # time.sleep(.01)

  def calculate_light(self):
    pass
    # dx = 10
    # # dy = 10
    # foo = [[]] * dx
    # for cell_id, cell in self.cells.items()
    #   i = int(cell.node.p[0]/800)
    #   foo[i].append((cell_id, cell.))

  def step(self, screen):
    # self.spread_morphogens()
    outputs = [(cell, cell.activate()) for cell in self.cells.values()]
    for cell, cell_out in outputs:
      if cell_out['apoptosis'] == True:
        self.graph.remove_node(cell.node.id)
        del self.cells[cell.id]

      if cell_out['growth'] != None:
        cell_type = cell_out['growth']
        r = 5
        dd = Vector(*cell_out['growth_direction']) * r
        daughter = self.add_cell(dd + cell.node.p.copy(), cell_type)
        for i, m in enumerate(cell.morphogens):
          daughter.morphogens[i] += m/2
          cell.morphogens[i] /= 2

      for i, m in enumerate(cell_out['morphogens']):
        cell.morphogens[i] += m

    if len(self.cells) == 0:
      return

    if self.draw:
      self.FD.run(self.plot)
    else:
      self.FD.run()

  def run(self, generations, screen=None):
    print('RUNNING')
    for gen in range(generations):
      self.step(screen)
      if len(self.cells) > 50:
        break

# Simulate a random genomes
if __name__ == '__main__':
  import os
  from neat import nn, parallel, population, visualize
  from neat.config import Config
  from cellGenome import CellGenome

  local_dir = os.path.dirname(__file__)
  config    = Config(os.path.join(local_dir, 'config.txt'))
  genome = CellGenome.create_unconnected(1, config)
  print(type(genome))
  print(genome)

  sim = Simulation(genome, (800,800))
  sim.run(10)
