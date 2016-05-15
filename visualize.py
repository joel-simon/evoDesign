from Vector import Vector
from scipy.spatial import Voronoi
import time
import numpy as np
import pygame
import pygame.gfxdraw
pygame.init()
screen = pygame.display.set_mode((800, 800))
from physics import VoronoiSpringPhysics

class VisualVoronoiSpringPhysics(VoronoiSpringPhysics):
  """docstring for VisualVoronoiSpringPhysics"""
  def __init__(self, *args, **kwargs):
    super(VisualVoronoiSpringPhysics, self).__init__(*args, **kwargs)

  def plot(self):
    map_pos = lambda p: (int(p[0]), 800-int(p[1]))
    points = [n.p for n in self.nodes]

    screen.fill((255,255,255))

    for point in points:
      x, y = map_pos(point)
      # pygame.gfxdraw.filled_circle(screen, x, y, 3, (10,10,10))
      pygame.gfxdraw.filled_circle(screen, x, y, 3, (10,10,10))

    for (node1, node2) in self.edges():
      x1, y1 = map_pos(node1.p)
      x2, y2 = map_pos(node2.p)
      pygame.gfxdraw.line(screen, x1, y1, x2, y2, (10,10,10))

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
    # time.sleep(.1)

  def step(self):
    super(VisualVoronoiSpringPhysics, self).step()
    self.plot()

# if __name__ == '__main__':


    # root = random.choice(FD.nodes)
    # FD.run(plot)
    # for node in FD.nodes.values():
    #   if node.p[1] < 5:
    #     node.static = True
    # while True:
    #   FD.add_node(Vector(root.p[0], root.p[1]-2))
    #   FD.run(plot)
    #   # foo = True
    #   for event in pygame.event.get():
    #     # if event.type == pygame.KEYDOWN:
    #     #   if event.key == pygame.K_DOWN and foo:
    #     if event.type == pygame.MOUSEBUTTONUP:
    #       x, y = pygame.mouse.get_pos()
    #       FD.add_node(Vector(x, 800-y))
    #       # FD.run(plot)
    #       # p = random.choice(graph.nodes).p.copy()
    #       # graph.add_node(root.p)

    #     if event.type == pygame.QUIT:
    #       sys.exit()
