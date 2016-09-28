import math
import time
from copy import copy

SQRT3 = math.sqrt( 3 )
import numpy as np

joint_offsets = [(0,0,0), (1,0,0), (1, 0, 1), (0, 0, 1),
                 (0,1,0), (1,1,0), (1, 1, 1), (0, 1, 1)]

class CellBody(object):
    """docstring for RigidBody"""
    def __init__(self, ID, truss, position, joint_map):
        self.ID = ID
        self.joints = [None] * 8
        self.members = []
        self.truss = truss
        self.position = position
        self.userData = dict()
        self.joint_map = joint_map
        # self.diagonals = []
        x, y, z = position
        # All joint positions based off center.
        positions = [
            [x-.5, y-.5, z-.5],
            [x+.5, y-.5, z-.5],
            [x+.5, y-.5, z+.5],
            [x-.5, y-.5, z+.5],
            [x-.5, y+.5, z-.5],
            [x+.5, y+.5, z-.5],
            [x+.5, y+.5, z+.5],
            [x-.5, y+.5, z+.5],
        ]

        for i, p in enumerate(joint_offsets):
            _x = p[0] + x
            _y = p[1] + y
            _z = p[2] + z
            joint = joint_map[_x][_y][_z] 
            if joint and joint.alive:
                self.joints[i] = joint
                self.joints[i].userData['parents'].add(self.ID)
            else:
                if _y <= 0:
                    self.joints[i] = truss.add_support(positions[i])
                else:
                    self.joints[i] = truss.add_joint(positions[i])

                joint_map[_x][_y][_z] = self.joints[i]
                self.joints[i].userData['parents'] = set([self.ID])

        assert(None not in self.joints)

        for i in range(4):
            self.add_member(self.joints[i], self.joints[(i+1)%4])
            self.add_member(self.joints[i + 4], self.joints[(i+1)%4 + 4])
            self.add_member(self.joints[i], self.joints[i+4])

        for i in range(4):
            self.add_member(self.joints[i], self.joints[4+(i+5)%4]) # diagonals
        self.add_member(self.joints[0], self.joints[2])
        self.add_member(self.joints[5], self.joints[7])
        
        # Inner diagonals
        # self.add_member(self.joints[0], self.joints[6])
        # self.add_member(self.joints[4], self.joints[2])
        # self.add_member(self.joints[1], self.joints[7])
        # self.add_member(self.joints[3], self.joints[5])


    def add_member(self, joint_a, joint_b):
        member = self.truss.member_between(joint_a, joint_b)
        if member is None:
            member = self.truss.add_member(joint_a, joint_b)
        self.members.append(member)
        return member

    def destroy(self):
        # Destroy any joint thats not part of another cell
        for joint in self.joints:
            joint.userData['parents'].remove(self.ID)
            if len(joint.userData['parents']) == 0:
                self.truss.destroy_joint(joint)

        # destroy members, some were alreayd destroyed above.
        for member in self.members[-6:]: # diagonal elements
            if member.alive:
                self.truss.destroy_member(member)
        for member in self.members:
            if member.alive:
                a = member.joint_a.userData['parents']
                b = member.joint_b.userData['parents']
                if len(a.intersection(b)) == 0:
                    self.truss.destroy_member(member)
