import math
import time
from copy import copy

SQRT3 = math.sqrt( 3 )
import numpy as np
class HexBody(object):
    """docstring for RigidBody"""
    def __init__(self, ID, truss, position, radius, neighbors, static):
        self.ID = ID
        self.joints = dict()
        self.members = []
        self.truss = truss
        self.radius = radius
        self.position = position

        positions = {
            'right': np.array([ radius+position[0], 0 +position[1], 0]),
            'top_right': np.array([.5 * radius+position[0], SQRT3 * radius /2+position[1], 0]),
            'top_left': np.array([-.5 * radius+position[0], SQRT3 * radius /2+position[1], 0]),
            'left': np.array([ -radius+position[0], 0 +position[1], 0]),
            'bottom_left': np.array([-.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1], 0]),
            'bottom_right': np.array([.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1], 0]),
        }

        for k in positions.keys():
            positions[k][0] += radius
            positions[k][1] += SQRT3 * radius / 2

        self.userData = dict()

        if neighbors[0]:# 'top_right':
            self.joints['top_right'] = neighbors[0].joints['left']
            self.joints['right'] = neighbors[0].joints['bottom_left']

        if neighbors[1]: # top
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

        for pos in positions.keys():
            s = static & 1
            static = static >> 1
            if pos not in self.joints:
                if s:
                    self.joints[pos] = truss.add_support(positions[pos])
                else:
                    self.joints[pos] = truss.add_joint(positions[pos])
            elif s:
                truss.make_static(self.joints[pos])

        assert(len(set(self.joints.keys())) == 6)

        for joint in self.joints.values():
            if 'parents' in joint.userData:
                joint.userData['parents'].add(self.ID)
            else:
                joint.userData['parents'] = set([self.ID])

        self.add_member(self.joints['top_left'], self.joints['top_right'])
        self.add_member(self.joints['top_right'], self.joints['right'])
        self.add_member(self.joints['right'], self.joints['bottom_right'])
        self.add_member(self.joints['bottom_right'], self.joints['bottom_left'])
        self.add_member(self.joints['bottom_left'], self.joints['left'])
        self.add_member(self.joints['left'], self.joints['top_left'])

        self.inner_members = [
            self.add_member(self.joints['top_left'], self.joints['bottom_left']),
            self.add_member(self.joints['top_left'], self.joints['bottom_right']),
            self.add_member(self.joints['bottom_right'], self.joints['top_right']),
        ]

    def add_member(self, joint_a, joint_b):
        member = self.truss.member_between(joint_a, joint_b)
        if member is None:
            member = self.truss.add_member(joint_a, joint_b)
        self.members.append(member)
        return member

    def destroy(self):
        # Destroy any joint thats not part of another cell
        for joint in self.joints.values():
            joint.userData['parents'].remove(self.ID)
            if len(joint.userData['parents']) == 0:
                self.truss.destroy_joint(joint)

        # destroy members, some were alreayd destroyed above.
        for member in self.members:
            if member.alive:
                a = member.joint_a.userData['parents']# == 1
                b = member.joint_b.userData['parents']# == 1
                if len(a.intersection(b)) == 0:
                    self.truss.destroy_member(member)
