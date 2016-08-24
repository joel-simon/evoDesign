import math
import random
import time
from copy import copy

from .vector import Vect2D

SQRT3 = math.sqrt( 3 )
# def hex_points(x, y, radius):
#     hex_coords = [( .5 * radius, 0 ),
#         ( 1.5 * radius, 0 ),
#         ( 2 * radius, SQRT3 / 2 * radius ),
#         ( 1.5 * radius, SQRT3 * radius ),
#         ( .5 * radius, SQRT3 * radius ),
#         ( 0, SQRT3 / 2 * radius ),
#         ( .5 * radius, 0 )
#     ]
#     return [((x + _x), ( y + _y)) for ( _x, _y ) in hex_coords]

class HexBody(object):
    """docstring for RigidBody"""
    def __init__(self, ID, world, position, radius, neighbors, static):
        # TODO make bodies a list
        self.ID = ID
        self.bodies = dict()
        self.joints = []
        self.world = world
        self.radius = radius
        self.position = position

        positions = {
            'top_right': (.5 * radius+position[0], SQRT3 * radius /2+position[1]),
            'top_left': (-.5 * radius+position[0], SQRT3 * radius /2+position[1]),
            'left': ( -radius+position[0], 0 +position[1]),
            'bottom_left': (-.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1]),
            'bottom_right': (.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1]),
            'right': ( radius+position[0], 0 +position[1]),
        }
        self.userData = dict()

        if neighbors[2]:# 'top_left':
            self.bodies['left'] = neighbors[2].bodies['bottom_right']
            self.bodies['top_left'] = neighbors[2].bodies['right']

        if neighbors[1]: #Top
            self.bodies['top_left'] = neighbors[1].bodies['bottom_left']
            self.bodies['top_right'] = neighbors[1].bodies['bottom_right']

        if neighbors[0]:# 'top_right':
            self.bodies['top_right'] = neighbors[0].bodies['left']
            self.bodies['right'] = neighbors[0].bodies['bottom_left']

        if neighbors[5]:# 'bottom_right':
            self.bodies['right'] = neighbors[5].bodies['top_left']
            self.bodies['bottom_right'] = neighbors[5].bodies['left']

        if neighbors[4]:# 'bottom':
            self.bodies['bottom_right'] = neighbors[4].bodies['top_right']
            self.bodies['bottom_left'] = neighbors[4].bodies['top_left']

        if neighbors[3]:# 'bottom_left':
            self.bodies['left'] = neighbors[3].bodies['top_right']
            self.bodies['bottom_left'] = neighbors[3].bodies['right']

        for derp in positions.keys():
            if derp not in self.bodies:
                self.bodies[derp] = self.create_body(positions[derp], static)

        assert(len(set(self.bodies.keys())) == 6)

        for body in self.bodies.values():
            body.userData['parents'].add(self.ID)

        self.create_joint(self.bodies['top_left'], self.bodies['top_right'])
        self.create_joint(self.bodies['top_right'], self.bodies['right'])
        self.create_joint(self.bodies['right'], self.bodies['bottom_right'])
        self.create_joint(self.bodies['bottom_right'], self.bodies['bottom_left'])
        self.create_joint(self.bodies['bottom_left'], self.bodies['left'])
        self.create_joint(self.bodies['left'], self.bodies['top_left'])

        a = self.create_joint(self.bodies['top_left'], self.bodies['bottom_left'])
        b = self.create_joint(self.bodies['top_left'], self.bodies['bottom_right'])
        c = self.create_joint(self.bodies['bottom_right'], self.bodies['top_right'])
        self.inner_joints = [a, b, c]

        # self.create_joint(self.bodies['top_right'], self.bodies['bottom_left'], hz=0)
        # self.create_joint(self.bodies['left'], self.bodies['right'], hz=0)

    def create_body(self, position, static):
        body_params = {
            'x': position[0],
            'y': position[1],
            'userData': {
                'origin': Vect2D(*position),
                'parents': set([self.ID])
                }
        }
        # print 'dict', dict(**body_params)
        if static:
            body = self.world.CreateStaticBody(**body_params)
        else:
            body = self.world.CreateDynamicBody(**body_params)
        #TODO make create_body automatically add to self.bodies
        return body

    def destroy(self):
        for joint in self.joints:
            assert(joint in self.world.joints)
        self.world.check_valid()
        for joint in self.inner_joints:
            self.world.DestroyJoint(joint)
            self.joints.remove(joint)

        # assert(len(self.joints) == len(set(self.joints)))
        self.world.check_valid()
        for body in self.bodies.values():
            body.userData['parents'].remove(self.ID)
            if len(body.userData['parents']) == 0:
                self.world.DestroyBody(body)

        self.world.check_valid()

        for j in copy(self.joints):
            a = len(j.bodyA.userData['parents']) == 1
            b = len(j.bodyB.userData['parents']) == 1
            assert(j in self.joints)
            if a and b:
                self.world.DestroyJoint(j)

        self.world.check_valid()

    def create_joint(self, bodyA, bodyB):
        for joint in bodyA.joints:
            if joint.bodyA == bodyB or joint.bodyB == bodyB:
                return joint
        joint = self.world.CreateDistanceJoint(
            bodyA=bodyA,
            bodyB=bodyB,
        )
        self.joints.append(joint)
        return joint
