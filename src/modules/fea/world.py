from copy import copy
from evaluate import evaluate
import numpy as np
import time

class World(object):
    """docstring for World"""
    def __init__(self, gravity=-10):
        self.joints = []
        self.members = []

        self.gravity = gravity

        # Joint data
        self.coords = []
        self.reactions = []
        self.loads = []
        self.next_joint_id = 0

        # Member data
        self.connections = []
        self.con_to_member = dict()
        self.E = []
        self.A = []
        self.next_member_id = 0

    def create_support(self, position):
        return self.create_joint(position, [1, 1, 1])

    def create_joint(self, position, re=[0, 0, 1]):
        position = list(position)
        position.append(0)

        joint = Joint(self.next_joint_id)
        self.joints.append(joint)
        self.next_joint_id += 1

        self.coords.append(position)
        self.reactions.append(re)
        self.loads.append([0, -1000, 0])

        return self.joints[-1]

    def create_member(self, joint_a, joint_b, e=1e7, a=1):
        # TODO create custom error
        assert joint_a in self.joints
        assert joint_b in self.joints
        assert (joint_a.id, joint_b.id) not in self.con_to_member
        assert (joint_b.id, joint_a.id) not in self.con_to_member

        member = Member(self.next_member_id, joint_a, joint_b)

        self.members.append(member)
        self.next_member_id += 1
        self.connections.append((joint_a.id, joint_b.id))
        self.con_to_member[(joint_a.id, joint_b.id)] = member
        self.E.append(e)
        self.A.append(a)

        joint_a.members.append(member)
        joint_b.members.append(member)

        return member

    def member_between(self, joint_a, joint_b):
        if (joint_a.id, joint_b.id) in self.con_to_member:
            return self.con_to_member[(joint_a.id, joint_b.id)]

        if (joint_b.id, joint_a.id) in self.con_to_member:
            return self.con_to_member[(joint_b.id, joint_a.id)]

        return None

    # def destroy_member(self, member):
    #     idx = self.memebrs.index(member)

    #     member.joint_a.members.remove(member)
    #     member.joint_b.members.remove(member)

    #     del self.members[idx]
    #     del self.connections[idx]
    #     del self.E[idx]
    #     del self.A[idx]

    # def destroy_joint(self, joint):
    #     idx = self.joints.index(joint)

    #     for member in copy(joint.members):
    #         self.destroy_member(member)

    #     del self.coords[idx]
    #     del self.reactions[idx]
    #     del self.joints[idx]
    #     del self.loads[idx]

    def add_load(self, joint, x=0, y=0):
        idx = self.joints.index(joint)
        self.loads[idx][0] += x
        self.loads[idx][1] += y

    def evaluate(self):
        start = time.time()
        reactions = np.array(self.reactions, dtype=bool).T
        coords = np.array(self.coords, dtype='float32')
        loads = np.array(self.loads, dtype='float32')
        connections = np.array(self.connections, dtype='int32').T
        print('prepared evaluate in %f' % (time.time() - start))

        result = evaluate(reactions, coords, loads, connections, self.E, self.A)
        print('evaluate ran in %f' % (time.time() - start))
        return result

    def check_valid(self):
        """ Only used for debugging.
        """
        assert(len(self.E) == len(self.members))
        assert(len(self.A) == len(self.members))
        assert(len(self.connections) == len(self.members))

        assert(len(self.coords) == len(self.joints))
        assert(len(self.reactions) == len(self.joints))
        assert(len(self.loads) == len(self.joints))


class Member(object):
    """docstring for Member"""
    def __init__(self, id, joint_a, joint_b):
        self.id = id
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.userData = {}

class Joint(object):
    """docstring for Joint"""
    def __init__(self, id):
        self.id = id
        self.members = []
        self.userData = {}

_U = [
    np.array([  0.,0.,0.,0. ,
        0.        ,  13.93980997,  11.86941089,  10.57444335,
        9.51282904,   8.68487667,  23.89316462,  22.71051025,
        21.18839202,  19.87581715,  18.90801577,  31.73164284,
        31.12740758,  30.10651127,  29.06213913,  28.29214327,
        38.03834001,  37.53834001,  36.64257527,  35.84612595,  35.48301539]),
    np.array([  0.        ,   0.        ,   0.        ,   0.        ,
         0.        ,   2.35728871,  -1.62354189,  -2.51873618,
        -3.28615047,  -4.92886017,   3.14417834,  -1.97165225,
        -4.30411913,  -5.83863899,  -8.52976797,   3.2484136 ,
        -2.15922646,  -5.37995873,  -7.54635403, -10.66287439,
         3.2484136 ,  -2.26346172,  -5.97927415,  -8.47969278, -11.52598495]),
    np.array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
        0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.])]

if __name__ == '__main__':
    world = World()

    # for pos in np.array([[2,1,0],[2,0,0],[1,1,0],[1,0,0]])*50:
    #     world.create_joint(pos)

    # world.create_support([0,50,0])
    # world.create_support([0,0,0])

    # for con in [[5, 3], [1, 3],[6, 4],[4, 2],[4, 3],[2, 1],[6, 3],[5, 4],[4, 1],[3, 2]]:
    #     world.create_member(con[0]-1, con[1]-1)

    # world.add_load(1, y=-1e5)
    # world.add_load(3, y=-1e5)

    joints = []
    for row in range(5):
        joint_row = []
        for col in range(5):
            if row == 0:
                joint_row.append(world.create_support([col*50, row*50, 0]))
            else:
                joint_row.append(world.create_joint([col*50, row*50, 0]))
            if row > 0:
                world.create_member(joints[-1][col], joint_row[-1])
            if col > 0:
                world.create_member(joint_row[-2], joint_row[-1])
            if row > 0 and col > 0:
                world.create_member(joint_row[-1], joints[-1][col-1])
        joints.append(joint_row)

    for joint in world.joints:
        world.add_load(joint, x=1e5)

    F, U, R = world.evaluate()
    # print list(U)
    assert(np.allclose(U, _U))
    # render(world, F, U)
