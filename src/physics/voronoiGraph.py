import sys, time, math
import random

# from pyhull.delaunay import DelaunayTri
# import pyvoro

from collections import defaultdict
import warnings

def norm(x, y):
    return math.sqrt(x*x + y*y)

class PhysicsBody(object):
    def __init__(self, position, r):
        self.position = list(position)
        # self.velocity = [0., 0.]
        self.vx = 0.
        self.vy = 0.
        self.ax = 0.
        self.ay = 0.
        # self.acceleration = [0., 0.]
        self.r = r
        self.edges = set()
        self.m = 1.0
        self.userData = {}
        self.ms = 6000.0

    def apply_force(self, fx, fy):
        self.ax += fx / self.m
        self.ay += fy / self.m

    def magnetic_strength(self):
        return self.ms

    def add_edge(self, other):
        self.edges.add(other)

    def remove_edge(self, other):
        self.edges.remove(other)

    def grow(self, r):
        self.r += r

    def get_stress(self):
        return 1.0

    def divide(self, angle):
        self.r = math.sqrt(2 * self.r*self.r / math.pi)
        diff = (math.cos(angle)*self.r, math.sin(angle)*self.r)
        dx = self.position[0] + diff[0]
        dy = self.position[1] + diff[1]
        self.position[0] -= diff[0]
        self.position[1] -= diff[1]
        return PhysicsBody(position=(dx, dy), r=self.r)
    # def neighbors(self):
    #         raise NotImplementedError

    # def step(self):
    #         raise NotImplementedError

class VoronoiGraphPhysics(object):
    """docstring for VoronoiGraphPhysics"""
    def __init__(self, stiffness, repulsion, damping, verbose=False,
                minEnergyThreshold=1, timestep=0.3, max_steps=200, renderer=None):

        self.stiffness = stiffness
        self.repulsion = repulsion
        self.damping   = damping
        self.minEnergyThreshold = minEnergyThreshold
        self.timestep  = timestep
        self.max_steps = max_steps

        self.renderer = renderer
        self.verbose = verbose
        # self.friction = 1.0

        self.bodies = list()
        # self.id_nodes = dict()
        self.adjacencies = defaultdict(set)

    # def add_edge(self, node_a, node_b):
    #     self.adjacencies[node_a].add(node_b)
    #     self.adjacencies[node_b].add(node_a)

    # def remove_edge(self, node_a, node_b):
    #     self.adjacencies[node_a].remove(node_b)
    #     self.adjacencies[node_b].remove(node_a)

    # def clear_edges(self):
    #     self.adjacencies = defaultdict(set)
    #     for node in self.bodies:
    #         self.adjacencies[node]

    def _applyHookesLaw(self):
        for node1, node2 in self.edges():
            # d = node1.p - node2.p #the direction of the spring
            dx = node1.position[0] - node2.position[0]
            dy = node1.position[1] - node2.position[1]

            r = node1.r + node2.r

            d_norm = norm(dx, dy)

            displacement = r - d_norm

            if displacement > 0:
                forcex = (dx / d_norm) * self.stiffness #* displacement
                forcey = (dy / d_norm) * self.stiffness#* displacement

                node1.apply_force(forcex, forcey)
                node2.apply_force(-1*forcex, -1*forcey)

    def _apply_magnetism(self):
        for bodyA, bodyB in self.edges():
            # d = self._distance(bodyA, bodyB)
            dx = bodyA.position[0] - bodyB.position[0]
            dy = bodyA.position[1] - bodyB.position[1]

            d = norm(dx, dy)

            strength = bodyA.magnetic_strength() * bodyB.magnetic_strength()

            fx = (dx/d) * strength / (4 * math.pi * d * d)
            fy = (dy/d) * strength / (4 * math.pi * d * d)

            bodyB.apply_force(fx, fy)
            bodyA.apply_force(-1*fx, -1*fy)

            # force = strength /

    def _applyGravity(self):
        for node in self.bodies:
            node.applyForce(0.0, -5*node.m)

    def _totalEnergy(self):
        energy = 0.0
        for node in self.bodies:
            speed = node.vx + node.vy
            energy += 0.5 * node.m * speed * speed

        return energy

    def _updateVelocityAndPositions(self):
        for node in self.bodies:
            node.vx += node.ax * self.timestep
            node.vy += node.ay * self.timestep

            node.ax = 0
            node.ay = 0

            node.vx *= self.damping
            node.vy *= self.damping

            node.position[0] += node.vx * self.timestep
            node.position[1] += node.vy * self.timestep

    def _distance(self, node_a, node_b):
        return math.sqrt(((node_a.position[0] - node_b.position[0])**2) + ((node_a.position[1] - node_b.position[1])**2))

    def _intersecting(self, node_a, node_b):
        return self._distance(node_a, node_b) < (node_a.r + node_b.r)

    def _updateEdges(self):
        # self.clear_edges()
        # edges = self.edges()
        for node_a, node_b in list(self.edges()):
            if self._distance(node_a, node_b) > (node_a.r + node_b.r)*1.2:
                self.remove_edge(node_a, node_b)

        n = len(self.bodies)
        assert(n!=0)
        if n == 1:
            return
        elif n == 2:
            self.add_edge(self.bodies[0], self.bodies[1])
        elif n == 3:
            self.add_edge(self.bodies[0], self.bodies[1])
            self.add_edge(self.bodies[1], self.bodies[2])
            self.add_edge(self.bodies[2], self.bodies[0])

        else:
            P = [(n.position[0], n.position[1]) for n in self.bodies]

            # tri = DelaunayTri(nodes)
            id_nodes = {i: n for i, n in enumerate(self.bodies) }

            # for ia, ib, ic in tri.vertices:
            #     self.add_edge(id_nodes[ia], id_nodes[ib])
            #     self.add_edge(id_nodes[ib], id_nodes[ic])
            #     self.add_edge(id_nodes[ic], id_nodes[ia])

            cells = pyvoro.compute_2d_voronoi(
              P, # point positions
              [[-400., 400.], [-400., 400.]], # limits
              2.0, # block size
              # radii=[1.3, 1.4]
            )
            # print(cells)
            for cell, body in zip(cells, self.bodies):
                # print(cell['faces'])
                for face in cell['faces']:
                    if face['adjacent_cell'] >= 0:
                        self.add_edge(body, id_nodes[face['adjacent_cell']])

            # for ia, ib in cells.adjacency:
                # self.add_edge(id_nodes[ia], id_nodes[ib])
                # self.add_edge(id_nodes[ib], id_nodes[ic])
                # self.add_edge(id_nodes[ic], id_nodes[ia])

    def neighbors(self, body):
        return body.edges
        # return self.adjacencies[node]

    def edges(self):
        foo = set()
        for bodyA in self.bodies:
            for bodyB in bodyA.edges:
                if (bodyA, bodyB) not in foo and (bodyB, bodyA) not in foo:
                    foo.add((bodyA, bodyB))
                    yield (bodyA, bodyB)

    def add_edge(self, bodyA, bodyB):
        bodyA.add_edge(bodyB)
        bodyB.add_edge(bodyA)

    def remove_edge(self, bodyA, bodyB):
        bodyA.remove_edge(bodyB)
        bodyB.remove_edge(bodyA)

    def create_body(self, position, shape):
        body = PhysicsBody(position, shape[0])
        self.bodies.append(body)
        return body
        # self.adjacencies[body]

    def remove_body(self, body):
        # for neighbor in self.adjacencies[node]:
        #     self.adjacencies[neighbor].remove(node)
        self.bodies.remove(body)
        # del self.adjacencies[node]
        # del self.id_nodes[node.id]

    def divide_body(self, body, angle):
        print('dividing body')
        daughter_body = body.divide(angle)
        print('divided body')

        if daughter_body:
            self.bodies.append(daughter_body)
            return daughter_body

        else:
            return None

    def grow_body(self, cell_body, shape):
        cell_body.grow(shape[0])

    def step(self):
        assert(len(self.bodies) != 0)

        self._updateEdges()
        self._applyHookesLaw()
        self._apply_magnetism()
        # self._applyGravity()
        self._updateVelocityAndPositions()

        if self.renderer:
            self.renderer(self)

    def finished(self, steps):
        if len(self.bodies) == 0:
            return True

        avg_energy = self._totalEnergy() / float(len(self.bodies))
        print(avg_energy)

        if steps > self.max_steps:
            return True

        if (avg_energy < self.minEnergyThreshold and steps > 0):
            return True

        return False

    def run(self):
        if self.verbose:
            print('Physics Starting')
        steps = 0

        for node in self.bodies:
            node.stress = 0.0

        while not self.finished(steps):
            self.step()
            steps += 1

        if self.verbose:
            print('Physics done')


