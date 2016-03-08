import sys, time, math
import numpy as np
from Vector import Vector
import random
from pyhull.delaunay import DelaunayTri
from collections import defaultdict

screen = None

# from scipy.spatial import Voronoi
# import pygame
# import pygame.gfxdraw
# pygame.init()
# screen = pygame.display.set_mode((800, 800))

class Graph(object):
  """docstring for Graph"""
  def __init__(self, ):
    self.nodes = dict()
    self.node_set = dict()
    # self.edges = []

    # Node id -> set of adjacencie
    self.adjacencies = defaultdict(set)

    self.nextNodeId = 0
    self.nextEdgeId = 0

  def add_node(self, p, static=False):
    node = Node(self.nextNodeId, p)
    node.static = static
    self.nodes[node.id] = node
    self.node_set[node.id] = node
    self.nextNodeId += 1
    return node

  def add_edge(self, node1_id, node2_id):
    id_a = min(node1_id, node2_id)
    id_b = max(node1_id, node2_id)
    self.adjacencies[id_a].add(id_b)
    self.adjacencies[id_b].add(id_a)

  def add_edges(self, array):
    for (a,b) in array:
      self.add_edge(a, b)

  def clear_edges(self):
    self.adjacencies = defaultdict(set)

  def remove_node(self, node_id):
    for adjacency_node_id in self.adjacencies[node_id]:
      self.adjacencies[adjacency_node_id].remove(node_id)

    del self.adjacencies[node_id]

  def edges(self):
    for id1, neighbors in self.adjacencies.items():
      for id2 in neighbors:
        if id1 < id2:
          yield (self.nodes[id1], self.nodes[id2])

  def neighbors(self, node):
    for n_id in self.adjacencies[node.id]:
      yield self.nodes[n_id]

class Node(object):
  """docstring for Node"""
  def __init__(self, id, p, m = 10.0):
    self.id = id
    self.p = p
    self.m = m
    self.v = Vector(0,0)
    self.a = Vector(0,0)
    self.r = 16.0
    self.static = False

  def applyForce(self, f):
    if not self.static:
      self.a += f / self.m

class ForceDirected(object):
  """docstring for ForceDirected"""
  def __init__(self, graph, stiffness, repulsion, damping,
                  minEnergyThreshold=1, timestep=0.3):
    self.graph = graph
    self.stiffness = stiffness
    self.repulsion = repulsion
    self.damping   = damping
    self.timestep  = timestep
    self.minEnergyThreshold = minEnergyThreshold
    self.friction = 1.0
    self.step_i = 0

  def springForce(self, node1, node2):
    d = node1.p - node2.p #the direction of the spring
    d = Vector(d[0]*1.5, d[1])

    r = node1.r + node2.r

    if d.norm() > 2*r:
      return 0.0
    # d2 = node2.p - node1.p
    # angle = math.atan2(d2[1],d2[0]) / 2 * math.pi
    # derp = 0.05 + abs(math.cos(angle))

    # r *= derp
    displacement = r - d.norm()

    direction = d.normalize()
    force = direction * self.stiffness * displacement * 0.5
    return force

  def applyHookesLaw(self):
    for node1, node2 in self.graph.edges():
      force = self.springForce(node1, node2)
      node1.applyForce(1 * force)
      node2.applyForce(-1 * force)

  def applyGravity(self):
    for node in self.graph.nodes.values():
      node.applyForce(Vector(0.0, -5*node.m))

  def applyConstraints():
    for node in self.graph.nodes.values():
      x, y = node.p
      assert(type(x) == type(1.0))
      assert(type(y) == type(1.0))
      vx, vy = node.v

      if x < 0:
        x = 0
        if vx < 0:
          vx *= -1

      elif x > 800:
        x = 800
        if vx > 0:
          vx *= -1

      if y < 0:
        y = 0
        if vy < 0:
          vy *= -1

      elif y > 800:
        y = 800
        if vy > 0:
          vy *= -1
      node.p = Vector(x, y)
      node.v = Vector(vx, vy)

  def applyCoulombsLaw(self):
    for node_a in self.graph.nodes.values():
      for node_b in self.graph.nodes.values():
        if node_a == node_b: continue
        d = node_a.p - node_b.p
        distance = d.norm() + 0.1 # avoid mive forces at small distances (and divide by zero)
        direction = d.normalize()

        # apply force to each end point
        force = direction*(self.repulsion)/(distance * distance * 0.5)
        node_a.applyForce(force)
        node_b.applyForce(-1 * force)

  def totalEnergy(self):
    energy = 0.0
    for node in self.graph.nodes.values():
      speed = node.v.norm()
      energy += 0.5 * node.m * speed * speed

    return energy

  def updateVelocity(self, timestep):
    for node in self.graph.nodes.values():
      node.v += node.a * timestep
      node.v *= self.damping
      node.a = Vector(0,0)

      if node.v[0] + node.v[1] < 1:
        node.v = Vector(0,0)

  def updatePositions(self, timestep):
    for node in self.graph.nodes.values():
      node.p += node.v * timestep
      if node.p[1] < 0:
        node.p = Vector(node.p[0], 1.0)
        node.v = Vector(0.0, node.v[1]* -1.0)

  def updateEdges(self):
    self.graph.clear_edges()
    try:
      tri = DelaunayTri(np.array([n.p for n in self.graph.nodes.values()]))
      for ia, ib, ic in tri.vertices:
        self.graph.add_edges([(ia, ib), (ib, ic), (ic, ia)])
    except AttributeError:
      return
      # print(e)

  def step(self, renderer=None):
    # self.applyCoulombsLaw()
    self.applyHookesLaw()
    self.applyGravity()
    self.updateVelocity(self.timestep)
    self.updatePositions(self.timestep)
    self.updateEdges()
    if renderer != None:
      renderer(self.graph)
    self.step_i += 1

  def run(self, renderer=None):
    avg_energy = 0.0
    start_i = self.step_i
    while avg_energy > self.minEnergyThreshold or self.step_i - start_i < 2:
    # while self.step_i- start_i < 100:
      self.step(renderer)
      self.updateEdges()
      avg_energy = self.totalEnergy() / float(len(self.graph.nodes))
      # print(self.step_i, avg_energy)
    # print("Finished force diagram step:", self.step_i - start_i)

def plot(graph):
  map_pos = lambda p: (int(p[0]), 800-int(p[1]))

  screen.fill((255,255,255))

  points = np.array([n.p for n in graph.nodes.values()])
  for point in points:
    x, y = map_pos(point)
    pygame.gfxdraw.filled_circle(screen, x, y, 3, (10,10,10))

  for (node1, node2) in graph.edges():
    x1, y1 = map_pos(node1.p)
    x2, y2 = map_pos(node2.p)
    d = node1.p - node2.p #the direction of the spring
    d = Vector(d[0]*1.5, d[1])
    r = node1.r + node2.r
    if d.norm() < 2*r:

      pygame.gfxdraw.line(screen, x1, y1, x2, y2, (10,10,10))

  vor = Voronoi(points)
  verts = vor.vertices
  # print(vor.regions)
  for ii, region in enumerate(vor.regions):
    if len(region) > 2 and -1 not in region:
      pointlist = [map_pos(verts[i]) for i in region]
      pygame.gfxdraw.aapolygon(screen, pointlist ,(10,10,10))
    elif -1 in region and ii < 20:
      point = points[ii]
      x, y = map_pos(point)
      pygame.gfxdraw.filled_circle(screen, x, y, 4, (255,10,10))

  pygame.display.flip()
  time.sleep(.02)

if __name__ == '__main__':
  plotting = True

  graph = Graph()

  # for i in range(5):
  #   graph.add_node(Vector(400+400*(random.random()-.5), 400+400*(random.random()-.5)))

  for i in range(10):
    graph.add_node(Vector(400, i*10))
  for i in range(10):
    graph.add_node(Vector(420, i*10 + 5))

  # graph.nodes[0].static = True

  FD = ForceDirected(graph, stiffness=400.0, repulsion=400.0, damping=0.5, timestep = .1)
  FD.updateEdges()

  if not plotting:
    FD.run()
  else:
    from scipy.spatial import Voronoi
    import pygame
    import pygame.gfxdraw
    pygame.init()
    screen = pygame.display.set_mode((800, 800))

    root = random.choice(graph.nodes)
    FD.run(plot)
    for node in graph.nodes.values():
      if node.p[1] < 5:
        node.static = True
    while True:
      graph.add_node(Vector(root.p[0], root.p[1]-2))
      FD.run(plot)
      # foo = True
      for event in pygame.event.get():
        # if event.type == pygame.KEYDOWN:
        #   if event.key == pygame.K_DOWN and foo:
        if event.type == pygame.MOUSEBUTTONUP:
          x, y = pygame.mouse.get_pos()
          FD.graph.add_node(Vector(x, 800-y))
          # FD.run(plot)
          # p = random.choice(graph.nodes).p.copy()
          # graph.add_node(root.p)

        if event.type == pygame.QUIT:
          sys.exit()

