import numpy
import pyximport
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)

from src.modules.truss import evaluatex as evaluate
from src.modules.truss.handle_results import handle_results
from src.modules.truss.utilities import prepare

g = 9.80665
from copy import copy
import numpy as np
from array import array

PI = np.pi
# rho = 200
# elastic_modulus = 5e8
# Fy = 5e8

rho = 7800
elastic_modulus = 200*pow(10, 9)
Fy = 250*pow(10, 6)

class Member(object):
    def __init__(self, r, joint_a, joint_b):
        self.r = r
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.userData = {}
        self.fos = 0
        self.alive = True
        # self.mass = 0

class Joint(object):
    def __init__(self, coordinates, translation):
        self.userData = {}
        self.members = []
        self.loads = np.zeros((3,))
        self.translation = translation
        self.coordinates = coordinates
        self.deflections = np.zeros((3,))
        self.alive = True

    def is_static(self):
        return sum(self.translation) == 3

class Truss(object):
    def __init__(self, file_path=None):
        # truss data
        self.fos_yielding = 0
        self.fos_buckling = 0
        self.fos_total = 0
        self.condition = 0
        self.mass = 0

        self.members = []
        self.joints = []

        self.joint_to_idx = dict()

        if file_path is not None:
            self.load(file_path)

    def add_member(self, joint_a, joint_b, r):
        assert isinstance(joint_a, Joint)
        assert isinstance(joint_b, Joint)
        member = Member(r, joint_a, joint_b)
        joint_a.members.append(member)
        joint_b.members.append(member)
        self.members.append(member)
        return member

    def add_support(self, coordinates):
        return self.add_joint(coordinates, [1, 1, 1])

    def add_joint(self, coords, translation=[0, 0, 0]):
        coords = np.array(coords)
        joint = Joint(coords, translation)
        self.joint_to_idx[joint] = len(self.joints)
        self.joints.append(joint)
        return joint

    def destroy_joint(self, joint):
        index = self.joint_index(joint)
        del self.joints[index]
        for member in copy(joint.members):
            self.destroy_member(member)
        self.joint_to_idx = {j:i for i, j in enumerate(self.joints)}
        joint.alive = False

    # def is_static(self, joint):
    #     return self.translations[self.joint_index(joint)].sum() == 3

    def make_static(self, joint):
        self.translations[self.joint_index(joint)] = np.ones([3])

    def joint_index(self, joint):
        return self.joint_to_idx[joint]

    def destroy_member(self, member):
        index = self.members.index(member)
        member.joint_a.members.remove(member)
        member.joint_b.members.remove(member)

        del self.members[index]
        member.alive = False

    def member_between(self, joint_a, joint_b):
        for member in joint_a.members:
            if member in joint_b.members:
                return member
        return None

    def get_loads(self):
        return np.array([j.loads for j in self.joints], dtype='float64').T

    def get_elastic(self):
        return numpy.zeros((len(self.members)))+elastic_modulus

    def valid_info(self, truss_info):
        assert(truss_info['elastic_modulus'].shape == (len(self.members),))
        assert(truss_info['area'].shape == (len(self.members),))
        assert(truss_info['coordinates'].shape == (len(self.joints), 3))
        assert(truss_info['connections'].shape == (len(self.members), 2))
        assert(truss_info['reactions'].shape == (3, len(self.joints)))
        assert(truss_info['loads'].shape == (3, len(self.joints)))

    def get_results(self, truss_info):
        self.valid_info(truss_info)
        return evaluate.the_forces(**truss_info)

    def calc_fos(self):
        if len(self.joints) == 0:
            self.fos_buckling = 0
            self.fos_total = 0
            self.fos_yielding = 0
            return 0

        area, connections = prepare(self)
        # Make everything an array and put everything into a dict
        truss_info = {
            "elastic_modulus": self.get_elastic(),
            "coordinates": numpy.array([j.coordinates for j in self.joints],dtype='float64'),
            "connections": connections,
            "area": area,
            "reactions": np.array([j.translation for j in self.joints],dtype='float64').T,
            "loads": self.get_loads(),
        }

        self.foo(self.get_results(truss_info))

    def foo(self, results):
        handle_results(self, *results)

    def load(self, file_path):
        with open(file_path, 'r') as f:
            for idx, line in enumerate(f.readlines()):
                if line[0] == "J":
                    info = line.split()[1:]
                    self.add_joint(numpy.array(
                        [float(x) for x in info[:3]]))
                    self.joints[-1].translation = numpy.array(
                        [int(x) for x in info[3:]])
                elif line[0] == "M":
                    info = line.split()[1:]
                    joint_a = self.joints[int(info[0])]
                    joint_b = self.joints[int(info[1])]
                    self.add_member(joint_a, joint_b, float(info[2]))
                elif line[0] == "L":
                    info = line.split()[1:]
                    self.joints[int(info[0])].loads[0] = float(info[1])
                    self.joints[int(info[0])].loads[1] = float(info[2])
                    self.joints[int(info[0])].loads[2] = float(info[3])
                elif line[0] != "#" and not line.isspace():
                    raise ValueError("'"+line[0] +
                                     "' is not a valid line beginner.")

    def save(self, file_path):
        with open(file_path, "w") as f:
            # Do the joints
            load_string = ""
            for j in self.joints:
                f.write("J" + "\t"
                        + str(j.coordinates[0]) + "\t"
                        + str(j.coordinates[1]) + "\t"
                        + str(j.coordinates[2]) + "\t"
                        + str(j.translation[0]) + "\t"
                        + str(j.translation[1]) + "\t"
                        + str(j.translation[2]) + "\n")
                if numpy.sum(j.loads) != 0:
                    load_string += "L" + "\t"
                    load_string += str(self.joint_index(j)) + "\t"
                    load_string += str(j.loads[0]) + "\t"
                    load_string += str(j.loads[1]) + "\t"
                    load_string += str(j.loads[2]) + "\t"
                    load_string += "\n"

            # Do the members
            for m in self.members:
                f.write("M" + "\t"
                        + str(self.joint_index(m.joint_a)) + "\t"
                        + str(self.joint_index(m.joint_b)) + "\t"
                        + str(m.r)
                        )
                f.write("\n")
            f.write(load_string)

