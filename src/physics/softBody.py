import math
from math import pi
import random
import numpy as np
from Box2D import *
from . import PhysicsBody

deg2rad = 0.0174532925199432957
rad2deg = 57.295779513082320876

def angle_dist(a, b):
    return pi - abs(abs(a - b) - pi)

# print(foo(-pi/4, pi/4))
# print(pi/2)
class SoftBody(PhysicsBody):
    """docstring for SoftBody"""
    def __init__(self, world, position, radius, n_bodies, bodies=None):
        self.world = world
        self.damping = .8
        self.softness = 5000
        self.nuke_joints = []
        self.userData = dict()

        if bodies == None:
            self.radius = radius

            self.bodies = []
            self.joints = []

            self.initvolume = radius * radius * 180.0 * deg2rad
            self.node_radius = radius * math.pi / n_bodies

            x, y = position
            for a in np.linspace(0, 2*math.pi, n_bodies, endpoint=False):
                position=(math.cos(a)*radius + x, math.sin(a)*radius + y)
                self._create_body(position)

            self.add_joint(self.bodies[0], self.bodies[n_bodies-1])
            for i in range(1, n_bodies):
                self.add_joint(self.bodies[i], self.bodies[i-1])
        else:
            self.joints = []
            self.bodies = bodies
            self.node_radius = bodies[0].fixtures[0].shape.radius
            self.change_in_bodies()
            for body in self.bodies:
                body.userData['parent'] = self


    def _create_body(self, position):
        body = self.world.CreateDynamicBody(
            position=position,
            userData={'parent': self},
            fixedRotation = True,
            # linearDamping=.00
        )
        body.CreateCircleFixture(
            shape=b2CircleShape(radius=self.node_radius),
            # density=.01,
           friction=.4
        )
        self.bodies.append(body)
        return body

    def change_in_bodies(self):
        self.radius = len(self.bodies) * self.node_radius/ (180.0 * deg2rad )
        self.initvolume = self.radius * self.radius * 180.0 * deg2rad

    def add_joint(self, bodyA, bodyB, maxLength=None):
        if maxLength == None:
            maxLength = 2*self.node_radius

        joint = self.world.CreateRopeJoint(
            # frequencyHz=1.0,
            # dampingRatio=.4,
            bodyA=bodyA,
            bodyB=bodyB,
            localAnchorA=(0,0),
            localAnchorB=(0,0),
            collideConnected=True,
            maxLength = maxLength
        )
        self.joints.append(joint)

    def volume(self):
        positions = []
        for body in self.bodies:
            positions.append(body.position)
        positions.append(self.bodies[0].position)
        # get surface of the total Element
        volume = 0.0

        # for i in range(0, len(positions) - 1, 2):
        #     volume += positions[i + 1][0] * (positions[i + 2][1] - positions[i][1]) + \
        #                 positions[i + 1][1] * (positions[i][0] - positions[i + 2][0])

        n = len(positions)
        for i in range(n):
            j = (i + 1) % n
            volume += positions[i][0] * positions[j][1]
            volume -= positions[j][0] * positions[i][1]

        volume = abs(volume / 2)
        return volume

    def center(self):
        avg_pos = b2Vec2(0, 0)

        for body in self.bodies:
            avg_pos += body.position

        return avg_pos / len(self.bodies)

    def computeDynamics(self):
        positions = []
        velocities = []
        avg_vel = b2Vec2(0, 0)
        avg_pos = b2Vec2(0, 0)

        friction = 0.1

        for body in self.bodies:
            positions.append(body.position)
            velocities.append(body.linearVelocity)
            avg_vel += velocities[-1]
            avg_pos += positions[-1]

        avg_vel /= float(len(self.bodies))
        avg_pos /= float(len(self.bodies))

        volume = self.volume()

        force = 0
        if volume > 0:
            force = self.softness * (self.initvolume / volume - 1)

        for i in range(len(self.bodies)):
            body = self.bodies[i]
            force_vector = (body.position - avg_pos)
            force_vector.Normalize()

            rel_vel = velocities[i] - avg_vel
            friction = rel_vel * self.damping

            force_vector *= force
            force_vector -= friction

            # print(force_vector)
            body.ApplyForce(force=(force_vector[0], force_vector[1]), point=(0,0), wake=False)

    def grow(self):
        print('growing', self.initvolume)

        joint = random.choice(self.joints)
        bodyA = joint.bodyA
        bodyB = joint.bodyB

        self.nuke_joints.append(joint)
        self.joints.remove(joint)

        body = self.world.CreateDynamicBody(
            position=(bodyA.position+bodyB.position)/2,
            userData={'cell': self},
            fixedRotation = True,
        )
        body.CreateCircleFixture(
            shape=b2CircleShape(radius=self.node_radius,),
        )
        self.bodies.insert(self.bodies.index(bodyB), body)

        self.add_joint(bodyA, body)
        self.add_joint(body, bodyB)

        self.change_in_bodies()

        return joint

    def get_stress(self):
        return self.volume() / self.initvolume

    def awake(self):
        return True

    def destroy(self):
        for body in self.bodies:
            self.world.DestroyBody(body)
            body = None

    def step(self):
        self.computeDynamics()

    def order_bodies(self):
        center = self.center()
        def key(body):
            diff = body.position - center
            return math.atan2(diff[1], diff[0])
        self.bodies.sort(key = key)

    # Utility function used by divide to created nodes linkings two others.
    def _connect(self, bodyA, bodyB, k = .6):
        assert(bodyA in self.bodies)
        assert(bodyB in self.bodies)

        body_distance = (bodyA.position - bodyB.position).Normalize() * k

        num_new = max(1, math.floor(body_distance/(self.node_radius*2)))
        print('dist', body_distance, num_new)
        assert(num_new > 0)

        X = np.linspace(bodyB.position[0],bodyA.position[0],num_new, endpoint=False)
        Y = np.linspace(bodyB.position[1],bodyA.position[1],num_new, endpoint=False)

        bodies = []
        for pos in zip(X, Y):
            bodies.append(self._create_body(pos))

        self.add_joint(bodyB, bodies[0])
        self.add_joint(bodies[-1], bodyA)

        for i in range(0, num_new - 1):
            self.add_joint(bodies[i], bodies[i+1])

        self.change_in_bodies()

    def divide(self, angle=0):
        center = self.center()
        bodyA, bodyB = None, None
        min_a, min_b = 3, 3

        for body in self.bodies:
            diff = body.position - center
            body_angle = math.atan2(diff[1], diff[0])
            if angle_dist(body_angle, angle) < min_a:
                bodyA = body
                min_a = angle_dist(body_angle, angle)

            if angle_dist(body_angle, angle+pi) < min_b:
                bodyB = body
                min_b = angle_dist(body_angle, angle+pi)

        # The points to split the cell
        i, j = sorted((self.bodies.index(bodyA), self.bodies.index(bodyB)))

        # return
        other_bodies = self.bodies[:i] + self.bodies[j:]
        self.bodies = self.bodies[i:j]

        assert(len(other_bodies) > 0)
        assert(len(self.bodies) > 0)

            # if joint.bodyA == self.bodies[j] and joint.bodyB == self.bodies[j+1]:
            #     self.nuke_joints.append(joint)

        self._connect(self.bodies[0], self.bodies[-1])
        self.order_bodies()

        daughter = SoftBody(self.world, None, None, None, other_bodies)
        daughter._connect(other_bodies[0], other_bodies[-1])
        daughter.order_bodies()

        for joint in self.joints:
            parentA = joint.bodyA.userData['parent']
            parentB = joint.bodyB.userData['parent']
            if (parentA == daughter) and (parentB == daughter):
                daughter.joints.append(joint)
                self.joints.remove(joint)
            elif (parentA != parentB):
                self.nuke_joints.append(joint)

        # for joint in daughter.joints:
        #     self.joints.remove(joint)

        print(len(self.bodies), len(daughter.bodies))

        return daughter

