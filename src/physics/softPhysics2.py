from Box2D import *
import random
from .framework import Framework
import time
import math
from .softBody2 import SoftBody
from copy import copy
from src.cell import Cell

deg2rad = 0.0174532925199432957
rad2deg = 57.295779513082320876

class Simulation(Framework):
    """docstring for Simulation"""
    def __init__(self, genome, verbose=False, max_steps=200):
        super(Simulation, self).__init__()
        self.max_steps = max_steps
        self.verbose = verbose

        self.next_id = 0
        self.cells = []
        self.steps_since_change = 0

        self.joints = []
        self.contacts = []
        self.nuke_joints = []
        self.nuke_bodies = []



        self.nodes_per_body = 50
        self.break_thresshold = 1000

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
        body = SoftBody(self.world, position, size)
        self.cell_bodies.append(body)
        return body

    def create_static_box(self, position, dimensions):
      self.world.CreateStaticBody(
        position=position,
        shapes=b2PolygonShape(box=dimensions),
        userData='bounds'
      )

    def neighbors(self, node):
      result = []
      for joint in self.world.joints:
        if body_node[joint.bodyA] == node:
          result.append(joint.bodyB.userData)
        elif body_node[joint.bodyB] == node:
          result.append(joint.bodyA.userData)

    def BeginContact(self, contact):
        self.contacts.append(contact)

    def divide_body(self, body, angle):
        daughter_body = body.divide(angle)
        if daughter_body:
            self.cell_bodies.append(daughter_body)
            return daughter_body
        else:
            return None

    # Functions used by simulation
    def grow_body(self, body, D):
        body.grow(D)
        if body.area > 400:
            return self.divide_body(body, math.pi/2)
        return None

    def _collide(self, bodyA, bodyB):
        """ Merge bodyA into bodyB """
        parentsA = bodyA.userData['parents']
        parentsB = bodyB.userData['parents']

        foo = [j.other for j in bodyA.joints]
        bar = [j.other for j in bodyB.joints]
        if len(set(foo).intersection(set(bar))) == 0:
            return

        print('COLLIDING')
        # bodyA
        self.nuke_bodies.append(bodyA)
        for parent in parentsA:
            parent.bodies.remove(bodyA)
        bodyA.userData = None

        # bodyB
        parentsB.update(parentsA)
        for parent in parentsA:
            parent.bodies.append(bodyB)

        # joints
        for jointEdge in bodyA.joints:
            old_joint = jointEdge.joint

            new_joint = self.world.CreateDistanceJoint(
                frequencyHz=old_joint.frequency,
                dampingRatio=old_joint.dampingRatio,
                bodyA=jointEdge.other,
                bodyB=bodyB,
                localAnchorA=(0,0),
                localAnchorB=(0,0),
                collideConnected=False,
                length = old_joint.length,
                userData = copy(old_joint.userData),
            )

            self.nuke_joints.append(old_joint)

            for parent in old_joint.userData['parents']:
                parent.joints.remove(old_joint)
                parent.joints.append(new_joint)

        for joint in self.world.joints:
            assert(joint.userData != None)
        # self.bodies.append(other_body)
        # other_body.userData['parents'].update(self_body.userData['parents'])

        # self.nuke_bodies.append(self_body)
        # self.bodies.remove(self_body)
        # self_body.userData = None

    def run(self):
        if self.verbose:
            print('Physics: starting.')
        self.running = True
        self.stepCount = 0
        start = time.time()
        super(Simulation, self).run()
        if self.verbose:
            print('Physics: finished after %i.' % self.stepCount)

    def Step(self, settings):
        # changes_made = False
        # apoptosis = 0
        # division = 0

        # for cell in self.cells:
        #     cell.body.setup()
        kill_cells = []

        for cell in self.cells:
            outputs = cell.get_outputs()
            if outputs['apoptosis']:
                self.cell.body.destroy()
                self.kill_cells.append(cell)
                # cannot apoptosis and do other things.
                continue

            # Cell Growth
            # if outputs['grow']:
            self.grow_cell(cell, outputs['grow'])


            divides = [outputs['divide0'],outputs['divide1'],outputs['divide2'],outputs['divide3']]
            if max(divides) > .5:
                print('divide')
                # angles = np.linspace(0,2*math.pi,4,endpoint=False)
                angles = [ 0., 1.57079633,  3.14159265,  4.71238898]
                angle = angles[divides.index(max(divides))]
                self.divide_cell(cell, angle)
                division += 1
        # for contact in self.contacts:
        #     bodyA, bodyB = (contact.fixtureA.body, contact.fixtureB.body)

        #     if bodyA in self.nuke_bodies or bodyB in self.nuke_bodies:
        #         continue
            # if bodyA.userData == 'bounds' or bodyB.userData == 'bounds':
            #     continue
            # if bodyA.userData == None:
            #     print(bodyA)
            #     continue
            # if bodyB.userData == None:
            #     print(bodyB)
            #     continue
            # if len(bodyA.userData['parents'].intersection(bodyB.userData['parents'])) == 0:
            #     self._collide(bodyA, bodyB)

        # for body in self.world.bodies:
        #     body.awake = True



        for joint in self.world.joints:
            if joint.userData['destroy']:
                self.nuke_joints.append(joint)
                joint.userData = None
                joint = None
                continue

            if joint.userData['length'] != joint.length:
                joint.length = joint.userData['length']

            if joint.length >= joint.userData['max_length']:
                bodyA = joint.bodyA
                bodyB = joint.bodyB
                parent = joint.userData['parents'][0]

                position = (bodyA.position + bodyB.position)/2
                body = parent.create_body(position)

                body.userData['parents'] = copy(joint.userData['parents'])

                jointA = parent._create_joint(bodyA, body, length=joint.length/2)
                jointB = parent._create_joint(bodyB, body, length=joint.length/2)


        # for body in self.world.bodies:

        for cell in self.cell_bodies:
            for joint in cell.nuke_joints:
                self.world.DestroyJoint(joint)
                joint = None

            for body in cell.nuke_bodies:
                self.world.DestroyBody(body)
                body = None
            cell.nuke_joints = []
            cell.nuke_bodies = []

        for joint in self.nuke_joints:
            self.world.DestroyJoint(joint)
            joint = None
        for body in self.nuke_bodies:
            self.world.DestroyBody(body)
            body = None

        self.nuke_joints = []
        self.nuke_bodies = []

        self.contacts = []
        self.running = not self.finished()

        # for joint in self.world.joints:
        #     assert(joint.userData != None)
        #     assert(joint.userData['parents'] != None)
        #     for parent in joint.userData['parents']:
        #         assert(joint in parent.joints)

        for body in self.world.bodies:
            try:
                if body.userData != 'bounds':
                    assert(body.userData != None)
                    assert(body.userData['parents'] != None)
                    for parent in body.userData['parents']:
                        assert(body in parent.bodies)

            except AssertionError as e:
                print(body)
                self.world.DestroyBody(body)
                # raise e


        super(Simulation, self).Step(settings)

    # def finish(self):
