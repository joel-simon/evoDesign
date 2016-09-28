import numpy
import pyximport
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)

from src.modules.truss import evaluatex as evaluate
from src.modules.truss.handle_results import handle_results

g = 9.80665
from copy import copy
import numpy as np

PI = np.pi
rho = 200
elastic_modulus = 5e8
Fy = 5e8

def valid_info(truss_info):
    assert(truss_info['elastic_modulus'].shape == (len(self.members),))
    assert(truss_info['area'].shape == (len(self.members),))
    assert(truss_info['coordinates'].shape == (len(self.joints), 3))
    assert(truss_info['connections'].shape == (len(self.members), 2))
    assert(truss_info['reactions'].shape == (3, len(self.joints)))
    assert(truss_info['loads'].shape == (3, len(self.joints)))

class Member(object):
    def __init__(self, r, joint_a, joint_b):
        self.r = r
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.userData = {}
        self.fos = 0
        self.alive = True

class Joint(object):
    def __init__(self, coordinates):
        self.userData = {}
        self.members = []
        self.loads = np.zeros((3))
        self.reactions = np.zeros([3, 1])
        self.coordinates = coordinates
        # Deflections
        self.deflections = np.zeros([3, 1])
        self.alive = True


class Truss(object):
    def __init__(self):
        # truss data
        self.fos_yielding = 0
        self.fos_buckling = 0
        self.fos_total = 0
        self.condition = 0

        # Member data
        self.members = []
        self.radii = []
        # self.lengths = []
        self.moi = []# moments of inertias
        # self.buckling_constants = []
        self.areas = [] # cross sectional areas
        self.masses = []

        # Joint data
        self.joints = []
        self.coordinates = []
        self.translations = []
        # self.deflections = []

        self.joint_to_idx = dict()

    def add_member(self, joint_a, joint_b, r=.1):
        # moi = (PI/4)*r**4
        area = (PI*r*r)
        # LW = area * rho

        # end_a = self.coordinates[self.joint_index(joint_a)]
        # end_b = self.coordinates[self.joint_index(joint_b)]

        # length = numpy.linalg.norm(end_a - end_b)
        # mass = length * LW
        # buckling_constant = -((PI**2)*elastic_modulus*moi/(length**2))

        member = Member(r, joint_a, joint_b)

        self.radii.append(r)
        # self.lengths.append(length)
        # self.moi.append(moi)
        # self.buckling_constants.append(buckling_constant)
        self.areas.append(area)
        # self.masses.append(mass)
        joint_a.members.append(member)
        joint_b.members.append(member)
        self.members.append(member)

        return member

    def add_support(self, coordinates):
        return self.add_joint(coordinates, [1, 1, 1])

    def add_joint(self, coords, translation=[0, 0, 0]):
        coords = np.array(coords)
        joint = Joint(coords)

        self.coordinates.append(coords)
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
        # del self.lengths[index]
        # del self.moi[index]
        # del self.buckling_constants[index]
        del self.areas[index]
        # del self.masses[index]
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


        results = evaluate.the_forces(**truss_info)
        self.foo(results)

    def foo(self, results):
        handle_results(self, *results)

# def handle_results(truss, forces, deflections, reactions):
#     fos_total = 10000

#     lengths = []
#     for m, force in zip(truss.members, forces):
#         end_a = numpy.array(m.joint_a.coordinates)
#         end_b = numpy.array(m.joint_b.coordinates)
#         length = numpy.linalg.norm(end_a - end_b)
#         r = m.r
#         moi = (PI/4)*r**4
#         area = (PI*r*r)
#         LW = area * rho
#         mass = length * LW

#         if force != 0:
#             fos_yielding = Fy * area / abs(force)
#         else:
#             fos_yielding = 10000

#         if force != 0:
#             fos_buckling = -((PI**2)*elastic_modulus*moi/(length**2)) / force
#             if fos_buckling <=0:
#                 fos_buckling = 10000
#         else:
#             fos_buckling = 10000

#         if fos_yielding < fos_buckling:

#             fos = fos_yielding
#         else:
#             fos = fos_buckling

#         if fos < fos_total:
#             fos_total = fos

#         m.fos = fos

#     for i in range(len(truss.joints)):
#         for j in range(3):
#             if truss.translations[i][j]:
#                 truss.joints[i].reactions[j] = reactions[j, i]
#                 truss.joints[i].deflections[j] = 0.0
#             else:
#                 truss.joints[i].reactions[j] = 0.0
#                 truss.joints[i].deflections[j] = deflections[j, i]

#     truss.fos_total = fos_total

#     return

    # member_fos_yielding = Fy * truss_info['area'] / np.absolute(forces)
    # member_fos_yielding[np.isnan(member_fos_yielding)] = 10000
    # member_fos_buckling = self.buckling_constants / forces
    # member_fos_buckling[member_fos_buckling <=0 ] = 10000

    # members_fos = np.minimum(member_fos_yielding, member_fos_buckling)

    # self.fos_buckling = member_fos_buckling.min()
    # self.fos_yielding = member_fos_yielding.min()
    # self.fos_total = min(self.fos_buckling, self.fos_yielding)

    # for member, fos in zip(self.members, members_fos):
    #     member.fos = fos

    # for i in range(len(self.joints)):
        # for j in range(3):
        #     if self.translations[i][j]:
        #         self.joints[i].reactions[j] = reactions[j, i]
        #         self.joints[i].deflections[j] = 0.0
        #     else:
        #         self.joints[i].reactions[j] = 0.0
        #         self.joints[i].deflections[j] = deflections[j, i]

    # if self.condition > pow(10, 5):
    #     self.fos_total /= 100
