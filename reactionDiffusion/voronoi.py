# from Vector import Vector
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
# sys.path.append('../')
from scipy.spatial import Voronoi
import time
import numpy as np
import pygame
import pygame.gfxdraw
from visualize import VisualVoronoiSpringPhysics
from Vector import Vector
from neat.config import Confi

class Node(object):
  """docstring for Node"""
  def __init__(self, p):
    self.id = 1
    self.p = p
    self.m = 1
    self.v = Vector(0,0)
    self.a = Vector(0,0)
    self.static = False
    self.stress = 0.0
    self.r = 16.0

  def applyForce(self, f):
    self.stress += abs(f.norm())
    if not self.static:
      self.a += f / self.m

def main():
  pygame.init()
  screen = pygame.display.set_mode((800, 800))

  physics = VisualVoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                      damping=0.5, timestep = .05)
  
  physics.add_node(Node(Vector(400,400)))
  physics.add_node(Node(Vector(400,401)))
  physics.add_node(Node(Vector(400,402)))
  physics.run()
  print 'done'
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

  # for (node1, node2) in self.edges():
  #   x1, y1 = map_pos(node1.p)
  #   x2, y2 = map_pos(node2.p)
  #   pygame.gfxdraw.line(screen, x1, y1, x2, y2, (10,10,10))

  # vor = Voronoi(points)
  # verts = vor.vertices
  # print(vor.regions)
  # for ii, region in enumerate(vor.regions):
  #   if len(region) > 2 and -1 not in region:
  #     pointlist = [map_pos(verts[i]) for i in region]
  #     pygame.gfxdraw.aapolygon(screen, pointlist ,(10,10,10))
    # elif -1 in region and ii < 20:
    #   point = points[ii]
    #   x, y = map_pos(point)
    #   pygame.gfxdraw.filled_circle(screen, x, y, 4, (255,10,10))

  pygame.display.flip()
# main()
# Simulate a random genomes
if __name__ == '__main__':
  # import os
  # from neat import nn, parallel, population, visualize
  # from neat.config import Config
  # from cellGenome import CellGenome
  # from visualize import VisualVoronoiSpringPhysics
  # import pygame, sys

  local_dir = os.path.dirname(__file__)
  config  = Config(os.path.join(local_dir, 'config.txt'))
  dummy_genome = CellGenome.create_unconnected(1, config)
  print dummy_genome  
  # physics = VisualVoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
  #                                       damping=0.6, timestep = .05)

  # sim = Simulation(dummy_genome, physics, (800, 800), starting_size=100)
  # sim.run(5)
  # while True:
  #   for event in pygame.event.get():
  #     if event.type == pygame.QUIT:
  #       sys.exit()

