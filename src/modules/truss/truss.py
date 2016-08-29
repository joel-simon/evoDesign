import numpy
from src.modules.truss.joint import Joint
from src.modules.truss.member import Member
from src.modules.truss import evaluate
from src.modules.truss.physical_properties import g
import time
import os
import warnings

class DuplicateMember(Exception):
    pass

class Truss(object):

    def __init__(self, file_name=""):
        # Make a list to store members in
        self.members = []

        # Lookup member from joint id's.
        self.joint_to_member = dict()

        # Make a list to store joints in
        self.joints = []

        # Variables to store number of joints and members
        self.number_of_joints = 0
        self.number_of_members = 0

        # Variables to store truss characteristics
        self.mass = 0
        self.fos_yielding = 0
        self.fos_buckling = 0
        self.fos_total = 0
        self.limit_state = ''
        self.condition = 0

    def add_support(self, coordinates):
        return self.add_joint(coordinates, [1, 1, 1])

    def add_joint(self, coordinates, translation=[0, 0, 1]):
        assert(coordinates.shape == (3,))
        # Make the joint
        self.joints.append(Joint(coordinates, translation))
        self.joints[self.number_of_joints]
        self.joints[-1].idx = self.number_of_joints
        self.number_of_joints += 1
        return self.joints[-1]

    def add_member(self, joint_index_a, joint_index_b):
        if (joint_index_a, joint_index_b) in self.joint_to_member:
            raise DuplicateMember()

        if (joint_index_b, joint_index_a) in self.joint_to_member:
            raise DuplicateMember()

        # Make a member
        self.members.append(Member(self.joints[joint_index_a],
                                   self.joints[joint_index_b]))

        self.members[-1].idx = self.number_of_members

        # Update joints
        self.joints[joint_index_a].members.append(self.members[-1])
        self.joints[joint_index_b].members.append(self.members[-1])

        self.joint_to_member[(joint_index_a, joint_index_b)] = self.members[-1]

        self.number_of_members += 1

        return self.members[-1]

    def member_between(self, joint_index_a, joint_index_b):
        if (joint_index_a, joint_index_b) in self.joint_to_member:
            return self.joint_to_member[(joint_index_a, joint_index_b)]

        if (joint_index_b, joint_index_a) in self.joint_to_member:
            return self.joint_to_member[(joint_index_b, joint_index_a)]

        return None

    def calc_mass(self):
        self.mass = 0
        for m in self.members:
            self.mass += m.mass

    def set_load(self, joint_index, load):
        self.joints[joint_index].load = load

    def calc_fos(self):
        # Pull supports and add to D
        coordinates = []
        for j in self.joints:
            coordinates.append(j.coordinates)

        # Build Re
        reactions = numpy.zeros([3, self.number_of_joints])
        loads = numpy.zeros([3, self.number_of_joints])
        for i in range(len(self.joints)):
            reactions[0, i] = self.joints[i].translation[0]
            reactions[1, i] = self.joints[i].translation[1]
            reactions[2, i] = self.joints[i].translation[2]
            loads[0, i] = self.joints[i].loads[0]
            loads[1, i] = self.joints[i].loads[1]\
                - sum([m.mass/2.0*g for m in self.joints[i].members])
            loads[2, i] = self.joints[i].loads[2]

        # Pull out E and A
        elastic_modulus = []
        area = []
        connections = []
        for m in self.members:
            elastic_modulus.append(m.elastic_modulus)
            area.append(m.area)
            connections.append([j.idx for j in m.joints])

        # Make everything an array
        area = numpy.array(area)
        elastic_modulus = numpy.array(elastic_modulus)
        coordinates = numpy.array(coordinates).T
        connections = numpy.array(connections).T

        # Pull everything into a dict
        truss_info = {"elastic_modulus": elastic_modulus,
                      "coordinates": coordinates,
                      "connections": connections,
                      "reactions": reactions,
                      "loads": loads,
                      "area": area}

        forces, deflections, reactions = \
            evaluate.the_forces(truss_info)

        for i in range(self.number_of_members):
            self.members[i].set_force(forces[i])

        for i in range(self.number_of_joints):
            for j in range(3):
                if self.joints[i].translation[j]:
                    self.joints[i].reactions[j] = reactions[j, i]
                    self.joints[i].deflections[j] = 0.0
                else:
                    self.joints[i].reactions[j] = 0.0
                    self.joints[i].deflections[j] = deflections[j, i]

        # Pull out the member factors of safety
        self.fos_buckling = min([m.fos_buckling for m in self.members])
        self.fos_yielding = min([m.fos_yielding for m in self.members])

        # Get total FOS and limit state
        self.fos_total = min(self.fos_buckling, self.fos_yielding)
        if self.fos_buckling < self.fos_yielding:
            self.limit_state = 'buckling'
        else:
            self.limit_state = 'yielding'

        # if self.condition > pow(10, 5):
        #     warnings.warn("The condition number is " + str(self.condition)
        #                   + ". Results may be inaccurate.")
