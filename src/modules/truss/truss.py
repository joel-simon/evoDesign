import numpy
import pyximport
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)

from src.modules.truss import evaluatex as evaluate
g = 9.80665

from copy import copy

import numpy as np
# cimport numpy as np

# import cython
# cimport cython

# from libc.math cimport sqrt

PI = np.pi
rho = 200
elastic_modulus = 5e8
Fy = 5e8

# DTYPE = numpy.float64
# ctypedef numpy.float64_t DTYPE_t


def valid_info(truss_info):
    assert(truss_info['elastic_modulus'].shape == (len(self.members),))
    assert(truss_info['area'].shape == (len(self.members),))
    assert(truss_info['coordinates'].shape == (len(self.joints), 3))
    assert(truss_info['connections'].shape == (len(self.members), 2))
    assert(truss_info['reactions'].shape == (3, len(self.joints)))
    assert(truss_info['loads'].shape == (3, len(self.joints)))

class Member(object):
    # cdef Joint, joint_a, joint_b
    # cdef dict userData
    def __init__(self, joint_a, joint_b):
        self.userData = {}
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.fos = 0
        self.alive = True

class Joint(object):
    # cdef dict userData
    def __init__(self):
        self.userData = {}
        self.members = []
        self.loads = np.zeros((3))
        # Reactions
        self.reactions = np.zeros([3, 1])

        # Deflections
        self.deflections = np.zeros([3, 1])
        self.alive = True


class Truss(object):

    # cdef list members, joints, E, A, coordinates
    # cdef double mass, fos_buckling, fos_yielding, fos_total, condition

    def __init__(self):
        # truss data
        self.fos_yielding = 0
        self.fos_buckling = 0
        self.fos_total = 0
        self.condition = 0

        # Member data
        self.members = []
        self.radii = []
        self.lengths = []
        self.moi = []# moments of inertias
        self.buckling_constants = []
        self.areas = [] # cross sectional areas
        self.masses = []

        # Joint data
        self.joints = []
        self.coordinates = []
        self.translations = []
        # self.deflections = []

        self.joint_to_idx = dict()

    def add_member(self, joint_a, joint_b, r=.1):
        moi = (PI/4)*r**4
        area = (PI*r*r)
        LW = area * rho

        end_a = self.coordinates[self.joint_index(joint_a)]
        end_b = self.coordinates[self.joint_index(joint_b)]

        length = numpy.linalg.norm(end_a - end_b)
        mass = length * LW
        buckling_constant = -((PI**2)*elastic_modulus*moi/(length**2))

        member = Member(joint_a, joint_b)

        self.radii.append(r)
        self.lengths.append(length)
        self.moi.append(moi)
        self.buckling_constants.append(buckling_constant)
        self.areas.append(area)
        self.masses.append(mass)
        joint_a.members.append(member)
        joint_b.members.append(member)
        self.members.append(member)

        return member

    def add_support(self, coordinates):
        return self.add_joint(coordinates, [1, 1, 1])

    def add_joint(self, coords, translation=[0, 0, 1]):
        joint = Joint()

        self.coordinates.append(np.array(coords))
        self.translations.append(np.array(translation, dtype='float64'))
        self.joint_to_idx[joint] = len(self.joints)
        self.joints.append(joint)
        return joint

    def destroy_joint(self, joint):
        index = self.joint_index(joint)
        del self.joints[index]
        del self.coordinates[index]
        del self.translations[index]

        for member in copy(joint.members):
            self.destroy_member(member)

        self.joint_to_idx = {j:i for i, j in enumerate(self.joints)}

        joint.alive = False

    def is_static(self, joint):
        return self.translations[self.joint_index(joint)].sum() == 3

    def make_static(self, joint):
        self.translations[self.joint_index(joint)] = np.ones([3])

    def joint_index(self, joint):
        return self.joint_to_idx[joint]

    def destroy_member(self, member):
        index = self.members.index(member)
        member.joint_a.members.remove(member)
        member.joint_b.members.remove(member)

        del self.members[index]
        del self.radii[index]
        del self.lengths[index]
        del self.moi[index]
        del self.buckling_constants[index]
        del self.areas[index]
        del self.masses[index]
        member.alive = False

    def calc_mass(self):
        self.mass = sum(self.masses)

    def make_connections(self):
        connections = numpy.zeros((len(self.members), 2), dtype='int64')
        for i, member in enumerate(self.members):
            connections[i][0] = self.joint_index(member.joint_a)
            connections[i][1] = self.joint_index(member.joint_b)
        return connections

    def member_between(self, joint_a, joint_b):
        for member in joint_a.members:
            if member in joint_b.members:
                return member
        return None

    def calc_fos(self):
        if len(self.joints) == 0:
            self.fos_buckling = 0
            self.fos_total = 0
            self.fos_yielding = 0
            return 0

        connections = self.make_connections()

        # Make everything an array and put everything into a dict
        truss_info = {
            "elastic_modulus": numpy.zeros((len(self.members)))+elastic_modulus,
            "coordinates": numpy.array(self.coordinates),
            "connections": connections,
            "reactions": np.array(self.translations).T,
            "loads": np.array([j.loads for j in self.joints]).T,
            "area": numpy.array(self.areas)
        }

        forces, deflections, reactions = evaluate.the_forces(**truss_info)

        member_fos_yielding = Fy * truss_info['area'] / np.absolute(forces)
        member_fos_yielding[np.isnan(member_fos_yielding)] = 10000
        member_fos_buckling = self.buckling_constants / forces
        member_fos_buckling[member_fos_buckling <=0 ] = 10000

        members_fos = np.minimum(member_fos_yielding, member_fos_buckling)

        self.fos_buckling = member_fos_buckling.min()
        self.fos_yielding = member_fos_yielding.min()
        self.fos_total = min(self.fos_buckling, self.fos_yielding)

        for member, fos in zip(self.members, members_fos):
            member.fos = fos

        for i in range(len(self.joints)):
            for j in range(3):
                if self.translations[i][j]:
                    self.joints[i].reactions[j] = reactions[j, i]
                    self.joints[i].deflections[j] = 0.0
                else:
                    self.joints[i].reactions[j] = 0.0
                    self.joints[i].deflections[j] = deflections[j, i]

        if self.condition > pow(10, 5):
            self.fos_total /= 100
