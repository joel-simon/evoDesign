from Box2D import *
import random
from .framework import Framework
import time
import math
from .softBody import SoftBody

deg2rad = 0.0174532925199432957
rad2deg = 57.295779513082320876

# def physicsFactory(framework):
class SoftPhysics(Framework):
    """docstring for SoftPhysics"""
    def __init__(self, verbose=False, max_steps=200, renderer=None):
        super(SoftPhysics, self).__init__()
        self.damping = .3
        self.max_steps = max_steps
        self.verbose = verbose

        self.next_id = 0

        self.nuke_joints = []

        self.cell_bodies = []
        self.joints = []
        self.contacts = []

        self.nodes_per_body = 50
        self.break_thresshold = 1000

    def run(self):
        if self.verbose:
            print('Physics: starting.')
        self.running = True
        self.stepCount = 0
        start = time.time()
        super(SoftPhysics, self).run()
        if self.verbose:
            print('Physics: finished after %i.' % self.stepCount)

    def finished(self):
        if self.stepCount > self.max_steps:
            return True
        if sum(b.awake() for b in self.cell_bodies) == 0:
            return True
        return False

    def neighbors(self, body):
        pass
        # for jointEdge in body.joints:
        #     yield jointEdge.other

    def destroy_body(self, body):
        self.cell_bodies.remove(body)
        body.destroy()
        body = None

    def create_body(self, position, size):
        body = SoftBody(self.world, position, size[0], self.nodes_per_body)
        self.cell_bodies.append(body)
        return body

    def create_static_box(self, position, dimensions):
      self.world.CreateStaticBody(
        position=position,
        shapes=b2PolygonShape(box=dimensions),
      )

    # def neighbors(self, node):
    #   result = []
    #   for joint in self.world.joints:
    #     if body_node[joint.bodyA] == node:
    #       result.append(joint.bodyB.userData)
    #     elif body_node[joint.bodyB] == node:
    #       result.append(joint.bodyA.userData)

    #   return result

    def BeginContact(self, contact):
        self.contacts.append(contact)


    def divide(self, body):
        daughter_body = body.divide()
        self.cell_bodies.append(daughter_body)
        # pass
        # return daughter

    # Functions used by simulation
    def grow(self, body):
        joint = body.grow()
        # print('joint', joint)
        self.nuke_joints.append(joint)


    def Step(self, settings):
        for cell in self.cell_bodies:
            cell.step()
            for joint in cell.nuke_joints:
                cell.joints.remove(joint)
                self.world.DestroyJoint(joint)
                joint = None
            cell.nuke_joints = []

        for contact in self.contacts:
            bodyA, bodyB = (contact.fixtureA.body, contact.fixtureB.body)

            if not (bodyA.userData and  bodyB.userData):
                continue

            if bodyA.userData['parent'] != bodyB.userData['parent']:
                dfn = b2DistanceJointDef(
                    frequencyHz=15.0,
                    dampingRatio=2,
                    bodyA=bodyA,
                    bodyB=bodyB,
                    localAnchorA=(0,0),
                    localAnchorB=(0,0),
                    collideConnected=False
                )
                self.joints.append(self.world.CreateJoint(dfn))
        self.contacts = []

        for joint in self.joints:
            f = joint.GetReactionForce(50.).Normalize()
            if f > self.break_thresshold:
              self.world.DestroyJoint(joint)
              self.joints.remove(joint)
              joint = None

        for joint in self.nuke_joints:
            self.world.DestroyJoint(joint)
            joint = None

        self.nuke_joints = []
        self.contacts = []
        self.running = not self.finished()
        super(SoftPhysics, self).Step(settings)
