import sys, time, math
# import numpy as np
from Vector import Vector
import random
from pyhull.delaunay import DelaunayTri
from collections import defaultdict
import warnings

class VoronoiSpringPhysics(object):
  """docstring for VoronoiSpringPhysics"""
  def __init__(self, stiffness, repulsion, damping,
                minEnergyThreshold=1, timestep=0.3):

    self.stiffness = stiffness
    self.repulsion = repulsion
    self.damping   = damping
    self.minEnergyThreshold = minEnergyThreshold
    self.timestep  = timestep
    self.friction = 1.0
    self.nodes = list()
    self.id_nodes = dict()
    self.adjacencies = defaultdict(set)

  # def nodes(self):
  #   return list(self.adjacencies.keys())

  def add_node(self, node):
    self.nodes.append(node)
    self.adjacencies[node]
    self.id_nodes[node.id] = node

  def remove_node(self, node):
    for neighbor in self.adjacencies[node]:
      self.adjacencies[neighbor].remove(node)

    self.nodes.remove(node)
    del self.adjacencies[node]
    del self.id_nodes[node.id]

  def add_edge(self, node_a, node_b):
    self.adjacencies[node_a].add(node_b)
    self.adjacencies[node_b].add(node_a)

  def remove_edge(self, node_a, node_b):
    self.adjacencies[node_a].remove(node_b)
    self.adjacencies[node_b].remove(node_a)

  # def add_edges(self, array):
  #   for (a,b) in array:
  #     self.add_edge(a, b)

  def clear_edges(self):
    self.adjacencies = defaultdict(set)
    for node in self.nodes:
      self.adjacencies[node]

  def neighbors(self, node):
    return self.adjacencies[node]

  def edges(self):
    for node, neighbors in self.adjacencies.items():
      for neighbor in neighbors:
        if node.id < neighbor.id:
          yield (node, neighbor)

  def springForce(self, node1, node2):
    d = node1.p - node2.p #the direction of the spring
    d = Vector(d[0], d[1])

    r = node1.r + node2.r
    displacement = r - d.norm()
    direction = d.normalize()
    force = direction * self.stiffness * displacement * 0.5
    return force

  def applyHookesLaw(self):
    for node1, node2 in self.edges():
      force = self.springForce(node1, node2)
      node1.applyForce(1 * force)
      node2.applyForce(-1 * force)

  def applyGravity(self):
    for node in self.nodes:
      node.applyForce(Vector(0.0, -5*node.m))

  def applyConstraints():
    for node in self.nodes:
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

  def totalEnergy(self):
    energy = 0.0
    for node in self.nodes:
      speed = node.v.norm()
      energy += 0.5 * node.m * speed * speed

    return energy

  def updateVelocity(self):
    for node in self.nodes:
      node.v += node.a * self.timestep
      node.v *= self.damping
      node.a = Vector(0,0)

      # if node.v[0] + node.v[1] < 1:
      #   node.v = Vector(0,0)

  def updatePositions(self):
    for node in self.nodes:
      node.p += node.v * self.timestep
      # if node.p[1] < 0:
      #   node.p = Vector(node.p[0], 1.0)
      #   node.v = Vector(0.0, node.v[1]* -1.0)

  def updateEdges(self):
    self.clear_edges()
    n = len(self.nodes)
    assert(n!=0)
    # nodes = self.nodes.vl
    if n == 1:
      return
    elif n == 2:
      self.add_edge(self.nodes[0], self.nodes[1])
    elif n == 3:
      self.add_edge(self.nodes[0], self.nodes[1])
      self.add_edge(self.nodes[1], self.nodes[2])
      self.add_edge(self.nodes[2], self.nodes[0])

    else:
      nodes = [n.p for n in self.nodes]
      tri = DelaunayTri(nodes)

      id_nodes = {i: n for i, n in enumerate(self.nodes) }

      for ia, ib, ic in tri.vertices:
        self.add_edge(id_nodes[ia], id_nodes[ib])
        self.add_edge(id_nodes[ib], id_nodes[ic])
        self.add_edge(id_nodes[ic], id_nodes[ia])

  def step(self):
    assert(len(self.nodes) != 0)

    for node in self.nodes:
      node.stress = 0.0

    self.updateEdges()
    self.applyHookesLaw()
    # self.applyGravity()
    self.updateVelocity()
    self.updatePositions()

  def finished(self, steps):
    avg_energy = self.totalEnergy() / float(len(self.nodes))

    if steps > 200:
      return True

    if (avg_energy < self.minEnergyThreshold and steps > 0):
      return True

    return False

  def run(self):
    steps = 0

    while not self.finished(steps):
      self.step()
      steps += 1

    # print(self.steps, avg_energy)
    # print("Finished force diagram step:", steps, '\n')

