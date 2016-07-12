from collections import defaultdict
from Box2D import *

import random

from .framework import FrameworkBase, Framework, Keys
import time
import math

from . import PhysicsSystem
from .rigidBody import RigidBody

class RigidPhysics(Framework):
    """docstring for RigidPhysics"""
    def __init__(self, verbose=False, max_steps=200, renderer=None):
        super(RigidPhysics, self).__init__()
        self.damping = .3
        self.max_steps = max_steps
        self.verbose = verbose

        self.next_id = 0

        self.nuke_joints = []

        self.cell_bodies = []
        self.joints = []
        self.contacts = []

        self.nodes_per_body = 50
        self.break_thresshold = 1000000

        self.damping = 0.1
        self.friction = .2
        self.density = 1

    def get_id(self):
        self.next_id += 1
        return self.next_id

    def create_static_box(self, position, dimensions):
        self.world.CreateStaticBody(
            position=position,
            shapes=b2PolygonShape(box=dimensions),
        )

    def run(self):
        if self.verbose:
            print('Physics: starting.')
        self.running = True
        self.stepCount = 0
        start = time.time()
        super(RigidPhysics, self).run()
        if self.verbose:
            print('Physics: finished after %i.' % self.stepCount)

    def finished(self):
        if self.stepCount > self.max_steps:
            return True
        if sum(b.body.awake for b in self.cell_bodies) == 0:
            return True
        return False

    def neighbors(self, body):
        for jointEdge in body.joints:
            yield jointEdge.other

    def BeginContact(self, contact):
        self.contacts.append(contact)

    def clear_edges(self, body):
        for jointEdge in body.joints:
            self.destroy_joints.append(jointEdge.joint)
            self.joints.remove(jointEdge.joint)

    def Keyboard(self, key):
        if key == Keys.K_g:
            grow = random.choice(self.bodies)
            fixt = grow.fixtures[0]
            x = abs(fixt.shape.vertices[0][0])
            y = abs(fixt.shape.vertices[0][1])

            grow.DestroyFixture(fixt)
            grow.CreateFixture(b2FixtureDef(
                shape=b2PolygonShape(box=(x, y+.3)),
                density=4,
                friction=2
            ))
        # if key == Keys.K_s:
        #   self.split(self.bodies[0])

    def Step(self, settings):

        # for contact in self.contacts:
        #     bodyA, bodyB = (contact.fixtureA.body, contact.fixtureB.body)
        #     if bodyA.userData and bodyB.userData:
        #         joints = bodyA.userData['parent'].add_edge(bodyB.userData['parent'])
        #         if joints:
        #             print('Added joint from collision')
        #             self.joints.extend(joints)
                # Else a joint already exists
        mag_str = 100
        for bodyA in self.cell_bodies:
            for bodyB in self.cell_bodies:
                if bodyA != bodyB:
                    D = bodyA.body.position - bodyB.body.position
                    d = D.Normalize()
                    strength = mag_str*bodyA.body.mass * mag_str*bodyB.body.mass
                    # force = d *strength / (4 * math.pi * d * d)
                    fx = (D[0]/d) * strength / (4 * math.pi * d * d)
                    fy = (D[1]/d) * strength / (4 * math.pi * d * d)

                    # bodyB.apply_force(fx, fy)
                    # bodyA.apply_force(-1*fx, -1*fy)

                    bodyA.body.ApplyForce(force=(-fx, -fy), point=(0,0),wake=False)
                    bodyB.body.ApplyForce(force=(fx, fy), point=(0,0),wake=False)

        # Handle garbage collction for cell_bodies
        for cell in self.cell_bodies:
            cell.step()
            for joint in cell.nuke_joints:
                self.world.DestroyJoint(joint)
                joint = None
            cell.nuke_joints = []

        # for joint in self.joints:
        #     # print(joint)
        #     f = joint.GetReactionForce(60.).Normalize()
        #     if f > self.break_thresshold:
        #         self.joints.remove(joint)
        #         self.world.DestroyJoint(joint)
        #         joint = None

        for joint in self.nuke_joints:
            print('destroying joint')
            self.world.DestroyJoint(joint)
            joint = None

        self.contacts = []
        self.nuke_joints = []
        self.running = not self.finished()
        super(RigidPhysics, self).Step(settings)

        # vel = sum(b.linearVelocity.Normalize() for b in self.world.bodies)
        # print(vel)
        # for body in self.world.bodies:
        #   if body.linearVelocity.Normalize() < .01:
        #     body.awake = False
        # print(foo, iner)

        # for bodyA, bodyB in self.edges():
        #   d = bodyA.position - bodyB.position
        #   if d.Normalize() > 40:
        #     self.remove_edge(bodyA, bodyB)
            # d = (bodyA.position.x - bodyB.position.x)**2

    # Functions used by simulation
    def grow_body(self, cell_body, shape):
        cell_body.grow(shape)
        body = cell_body.body

        for joint in self.joints:
            if body == joint.bodyA:
                # print('derpa')
                self.nuke_joints.append(joint)
                self.joints.remove(joint)
                # cell_body.add_edge(joint.bodyB.userData['parent'])
            if  body == joint.bodyB:
                # print('derpa')

                self.nuke_joints.append(joint)
                self.joints.remove(joint)
                # cell_body.add_edge(joint.bodyA.userData['parent'])



        # fixt = body.fixtures[0]
        # d0 = 2*abs(fixt.shape.vertices[0][0])
        # d1 = 2*abs(fixt.shape.vertices[0][1])
        # self.set_size(body, d0+g0, d1+g1)

    def area(self, body):
        return body.area()
        # fixt = body.fixtures[0]
        # w = 2*abs(fixt.shape.vertices[0][0])
        # h = 2*abs(fixt.shape.vertices[0][1])
        # return w*h

    def remove_body(self, body):
        self.bodies.remove(body)
        self.world.DestroyBody(body)

    def create_body(self, position, shape):
        body = RigidBody(world=self.world,
                         # ID=self.get_id(),
                         position=position,
                         shape=shape,
                         density=self.density,
                         friction=self.friction,
                         damping=self.damping)
        self.cell_bodies.append(body)
        return body

    def divide_body(self, body, angle):
        daughter_body = body.divide(angle)
        if daughter_body:
            self.cell_bodies.append(daughter_body)

            for joint in self.joints:
                self.nuke_joints.append(joint)
                self.joints.remove(joint)

            return daughter_body
        else:
            return None

