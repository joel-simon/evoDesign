from Vector import Vector
from scipy.spatial import Voronoi
import time
import numpy as np
import pygame
import pygame.gfxdraw
pygame.init()
font = pygame.font.SysFont("monospace", 18)
screen = pygame.display.set_mode((800, 800))
from physics import VoronoiSpringPhysics
from os.path import join
import sys

def plot(nodes, edges):
  map_pos = lambda p: (int(p[0]), 800-int(p[1]))
  points = [(n.px, n.py) for n in nodes]

  screen.fill((255,255,255))

  c_a = [ n.morphogen_concentrations[0][0] for n in nodes ]
  c_b = [ n.morphogen_concentrations[0][1] for n in nodes ]

  m_range = (min(c_a), max(c_a))

  mintext = font.render("a range:(%f, %f)" % (min(c_a), max(c_a)),1,(0,0,0) )
  screen.blit(mintext, (10,10))

  mintext = font.render("b range:(%f, %f)" % (min(c_b), max(c_b)),1,(0,0,0) )
  screen.blit(mintext, (10,30))

  num_nodes = font.render("# nodes: %i" % len(nodes),1,(0,0,0) )
  screen.blit(num_nodes, (10,50))

  for node in nodes:
    x, y = map_pos((node.px, node.py))
    # print(node.px, node.py, x, y)
    pygame.gfxdraw.aacircle(screen, x, y, int(node.r), (10, 10, 10))
    a = node.morphogen_concentrations[0][0]

    red = int(200 * (a-m_range[0])/(1+m_range[1]-m_range[0]))
    # blue = int(255 * node.morphogen_concentrations[0][1])

    pygame.gfxdraw.filled_circle(screen, x, y, int(node.r), (200,10,10, red))

  for (node1, node2) in edges:
    x1, y1 = map_pos((node.px, node.py))
    x2, y2 = map_pos((node.px, node.py))
    pygame.gfxdraw.line(screen, x1, y1, x2, y2, (10,10,10))

  # vor = Voronoi(points)
  # verts = vor.vertices
  # for ii, region in enumerate(vor.regions):
  #   if len(region) > 2 and -1 not in region:
  #     pointlist = [map_pos(verts[i]) for i in region]
  #     pygame.gfxdraw.aapolygon(screen, pointlist, (10,10,10))
  #   elif -1 in region and ii < 20:
  #     point = points[ii]
  #     x, y = map_pos(point)
  #     pygame.gfxdraw.filled_circle(screen, x, y, 4, (255,10,10))

  pygame.display.flip()
  # time.sleep(1)


class VisualVoronoiSpringPhysics(VoronoiSpringPhysics):
  """docstring for VisualVoronoiSpringPhysics"""
  def __init__(self, *args, **kwargs):
    super(VisualVoronoiSpringPhysics, self).__init__(*args, **kwargs)

  def step(self):
    super(VisualVoronoiSpringPhysics, self).step()
    plot(self.nodes, self.edges())

def main(path):
  import pickle
  import sys
  import random
  from simulation import Simulation

  with open(join(path, 'population.p'), 'rb') as f:
    pop = pickle.load(f, encoding='latin1')

  physics = VisualVoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                        damping=0.4, timestep = .05)

  best_genome = pop.statistics.best_genome()
  # print('ready')
  sim = Simulation(best_genome, physics, (800, 800), verbose=True)

  # print('2')
  sim.run(80)
  print('run over')
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    main('./out')
  else:
    main(sys.argv[1])
