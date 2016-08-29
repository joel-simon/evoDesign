import math
import time
from copy import copy

SQRT3 = math.sqrt( 3 )
import numpy as np
class HexBody(object):
    """docstring for RigidBody"""
    def __init__(self, ID, truss, position, radius, neighbors, static):

        self.ID = ID
        self.joints = dict() # TODO make bodies a list
        self.members = []
        self.truss = truss
        self.radius = radius
        self.position = position

        positions = {
            'top_right': np.array([.5 * radius+position[0], SQRT3 * radius /2+position[1], 0]),
            'top_left': np.array([-.5 * radius+position[0], SQRT3 * radius /2+position[1], 0]),
            'left': np.array([ -radius+position[0], 0 +position[1], 0]),
            'bottom_left': np.array([-.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1], 0]),
            'bottom_right': np.array([.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1], 0]),
            'right': np.array([ radius+position[0], 0 +position[1], 0]),
        }

        for k in positions.keys():
            positions[k][0] += radius
            positions[k][1] += SQRT3 * radius / 2 

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
                    self.joints[derp] = truss.add_support(positions[derp])
                else:
                    self.joints[derp] = truss.add_joint(positions[derp])

        assert(len(set(self.joints.keys())) == 6)

        for joint in self.joints.values():
            if 'parents' in joint.userData:
                joint.userData['parents'].add(self.ID)
            else:
                joint.userData['parents'] = set([self.ID])

        self.members.append(self.add_member(truss, self.joints['top_left'], self.joints['top_right']))
        self.members.append(self.add_member(truss, self.joints['top_right'], self.joints['right']))
        self.members.append(self.add_member(truss, self.joints['right'], self.joints['bottom_right']))
        self.members.append(self.add_member(truss, self.joints['bottom_right'], self.joints['bottom_left']))
        self.members.append(self.add_member(truss, self.joints['bottom_left'], self.joints['left']))
        self.members.append(self.add_member(truss, self.joints['left'], self.joints['top_left']))

        self.members.append(self.add_member(truss, self.joints['top_left'], self.joints['bottom_left']))
        self.members.append(self.add_member(truss, self.joints['top_left'], self.joints['bottom_right']))
        self.members.append(self.add_member(truss, self.joints['bottom_right'], self.joints['top_right']))

    def add_member(self, truss, joint_a, joint_b):
        member = truss.member_between(joint_a.idx, joint_b.idx)
        if member is not None:
            return member
        else:
            return truss.add_member(joint_a.idx, joint_b.idx)

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

