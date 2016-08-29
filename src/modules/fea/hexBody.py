import math
import time
from copy import copy

SQRT3 = math.sqrt( 3 )

class HexBody(object):
    """docstring for RigidBody"""
    def __init__(self, ID, world, position, radius, neighbors, static):

        self.ID = ID
        self.joints = dict() # TODO make bodies a list
        self.members = []
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

        if neighbors[0]:# 'top_right':
            self.joints['top_right'] = neighbors[0].joints['left']
            self.joints['right'] = neighbors[0].joints['bottom_left']

        if neighbors[1]: #Top
            self.joints['top_left'] = neighbors[1].joints['bottom_left']
            self.joints['top_right'] = neighbors[1].joints['bottom_right']

        if neighbors[2]:# 'top_left':
            self.joints['left'] = neighbors[2].joints['bottom_right']
            self.joints['top_left'] = neighbors[2].joints['right']

        if neighbors[3]:# 'bottom_left':
            self.joints['left'] = neighbors[3].joints['top_right']
            self.joints['bottom_left'] = neighbors[3].joints['right']

        if neighbors[4]:# 'bottom':
            self.joints['bottom_right'] = neighbors[4].joints['top_right']
            self.joints['bottom_left'] = neighbors[4].joints['top_left']

        if neighbors[5]:# 'bottom_right':
            self.joints['right'] = neighbors[5].joints['top_left']
            self.joints['bottom_right'] = neighbors[5].joints['left']


        for derp in positions.keys():
            if derp not in self.joints:
                if static:
                    self.joints[derp] = world.create_support(positions[derp])
                else:
                    self.joints[derp] = world.create_joint(positions[derp])

        assert(len(set(self.joints.keys())) == 6)

        for joint in self.joints.values():
            if 'parents' in joint.userData:
                joint.userData['parents'].add(self.ID)
            else:
                joint.userData['parents'] = set([self.ID])

        self.members.append(self.get_or_create_member(world, self.joints['top_left'], self.joints['top_right']))
        self.members.append(self.get_or_create_member(world, self.joints['top_right'], self.joints['right']))
        self.members.append(self.get_or_create_member(world, self.joints['right'], self.joints['bottom_right']))
        self.members.append(self.get_or_create_member(world, self.joints['bottom_right'], self.joints['bottom_left']))
        self.members.append(self.get_or_create_member(world, self.joints['bottom_left'], self.joints['left']))
        self.members.append(self.get_or_create_member(world, self.joints['left'], self.joints['top_left']))

        self.members.append(self.get_or_create_member(world, self.joints['top_left'], self.joints['bottom_left']))
        self.members.append(self.get_or_create_member(world, self.joints['top_left'], self.joints['bottom_right']))
        self.members.append(self.get_or_create_member(world, self.joints['bottom_right'], self.joints['top_right']))

    def get_or_create_member(self, world, joint_a, joint_b):
        member = world.member_between(joint_a, joint_b)
        if member is not None:
            return member

        return world.create_member(joint_a, joint_b)

    def destroy(self):
        raise NotImplementedError()
        # for joint in self.joints:
        #     assert(joint in self.world.joints)
        # self.world.check_valid()
        # for joint in self.inner_joints:
        #     self.world.DestroyJoint(joint)
        #     self.joints.remove(joint)

        # # assert(len(self.joints) == len(set(self.joints)))
        # self.world.check_valid()
        # for body in self.joints.values():
        #     body.userData['parents'].remove(self.ID)
        #     if len(body.userData['parents']) == 0:
        #         self.world.DestroyBody(body)

        # self.world.check_valid()

        # for j in copy(self.joints):
        #     a = len(j.bodyA.userData['parents']) == 1
        #     b = len(j.bodyB.userData['parents']) == 1
        #     assert(j in self.joints)
        #     if a and b:
        #         self.world.DestroyJoint(j)

        # self.world.check_valid()

