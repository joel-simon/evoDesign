import math
from math import pi
import random
import numpy as np
from Box2D import *
from . import PhysicsBody
from copy import copy
import traceback
from collections import defaultdict

deg2rad = 0.0174532925199432957
rad2deg = 57.295779513082320876

def angular_distance(theta_1, theta_2, mod=2*math.pi):
    difference = abs(theta_1 % mod - theta_2 % mod)
    return min(difference, mod - difference)

def nearest_angle(L, theta):
    return min(L, key=lambda theta_1: angular_distance(theta, theta_1))

# def angle_dist(a, b):
#     return pi - abs(abs(a - b) - pi)

def angle_between(bodyA, bodyB):
    x = bodyA.position[0] - bodyB.position[0]
    y = bodyA.position[1] - bodyB.position[1]
    angle = math.atan2(y, x)
    if angle < 0:
        return 2*pi - abs(angle)
    else:
        return angle

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def distance(bodyA, bodyB):
    return (bodyA.position - bodyB.position).Normalize()

def joint_parents(joint):
    parentsA = joint.bodyA.userData['parents']
    parentsB = joint.bodyB.userData['parents']
    return parentsA.intersection(parentsB)

def pca(X):
  n_samples, n_features = X.shape
  X -= np.mean(X, axis=0)
  U, S, V = np.linalg.svd(X, full_matrices=False)
  explained_variance_ = (S ** 2) / n_samples
  explained_variance_ratio_ = (explained_variance_ /
                               explained_variance_.sum())
  return (V, explained_variance_ratio_)

NOTHING = object()

class SoftBody(PhysicsBody):
    body_id = 0
    """docstring for SoftBody"""
    def __init__(self, world, position, bodies, wall_length=1, verbose=False):
        self.world = world

        # attribtutes
        self.damping = 6
        self.friction = 1
        self.softness = 10000

        self.wall_length = wall_length
        self.max_wall_length = self.wall_length * 2
        self.contracted_axis = None
        self.userData = dict()
        self.rest_area = None

        self.interal_body = False

        # Attributes to update every time step
        self.angle = 0 #Angle of major axis.
        self.center = (0,0)

        self.area = 0
        self.rest_area = None
        self.pressure = 0

        self.bodies = []
        self.inner_joints = []

        # body -> other bodies
        self.verbose = verbose

        if type(bodies) == type(1):
            c = bodies * wall_length
            r = c / (2*pi)
            # Create bodies
            x, y = position
            for a in np.linspace(0, 2*math.pi, bodies, endpoint=False):
                body_position=(x+math.cos(a)*r, y+math.sin(a)*r)
                body = self._create_body(body_position)
                self.bodies.append(body)

            # Create joints
            for i in range(0, bodies):
                joint = self._create_joint(self.bodies[i], self.bodies[i-1])
            self.rest_area = self._area()
            self.area=self.rest_area

        elif type(bodies) == type([]):
            self.bodies = bodies
            self.rest_area = self._area()
            self.area=self.rest_area

        # self.cent_body = self.world.CreateBody(
        #     position=tuple(self._center()),
        # )
        # fixt = self.cent_body.CreatePolygonFixture(
        #     box=[2, .2],
        # )
        # fixt.sensor = True

        self._create_inner_joints()
        # self._sort_bodies()

    # def _max_area(self):
    #     joints = self._get_joints()
    #     c = sum(j.length for j in joints)
    #     a = c * c / (4*pi)
    #     return a

    def _create_inner_joints(self):

        if len(self.inner_joints) > 0:
            self.nuke_joints.extend(self.inner_joints)

        self.inner_joints = []

        # for body in self.bodies:
        #     joint = self._create_joint(self.cent_body, body, hz=1, dr=.6, length=None)
        #     self.inner_joints.append(joint)

        # for i in range(0, len(self.corners)):
        #     joint = self._create_joint(self.corners[i], self.corners[i-1])
        #     self.inner_joints.append(joint)
        #     self.joints.remove(joint)

        # joint = self._create_joint(self.corners[0], self.corners[2])
        # self.inner_joints.append(joint)
        # self.joints.remove(joint)

        # joint = self._create_joint(self.corners[1], self.corners[3])
        # self.inner_joints.append(joint)
        # self.joints.remove(joint)

        return self.inner_joints

    def _create_body(self, position):
        body = self.world.CreateDynamicBody(
            position=position,
            fixedRotation = True,
            linearDamping=self.damping,
            userData={
                'id': SoftBody.body_id,
                'type': 'node',
                'parents': set([self]),
            },
        )
        SoftBody.body_id += 1
        body.CreateCircleFixture(
            shape=b2CircleShape(radius=self.wall_length/2),
            # density=.0,
            friction=self.friction
        )
        return body

    def _create_joint(self, bodyA, bodyB, hz=12, dr=.2, length=NOTHING, type='outer_wall'):
        joint = self.world.CreateDistanceJoint(
            frequencyHz=hz,
            dampingRatio=dr,
            bodyA=bodyA,
            bodyB=bodyB,
            localAnchorA=(0,0),
            localAnchorB=(0,0),
            collideConnected=False,
            userData = {
                'type': type,
                # 'parents': set([self]),
            },
        )

        if length == NOTHING:
            length = self.wall_length

        if length != None:
            joint.length = length

        joint.userData['length'] = joint.length
        # print(joint)
        return joint

    # def _destroy_joint(self, joint):


    def _area(self):
        """ The shoelace algorithm for polgon area """
        positions = []
        for body in self.bodies:
            positions.append(body.position)
        positions.append(self.bodies[0].position)
        # get surface of the total Element
        area = 0.0

        n = len(positions)
        for i in range(n):
            j = (i + 1) % n
            area += positions[i][0] * positions[j][1]
            area -= positions[j][0] * positions[i][1]

        area = abs(area / 2.)
        return area

    def _center(self):
        avg_pos = b2Vec2(0, 0)

        for body in self.bodies:
            avg_pos += body.position

        return avg_pos / len(self.bodies)

    def _computeDynamics(self):
        positions = []
        velocities = []
        avg_vel = b2Vec2(0, 0)
        avg_pos = b2Vec2(0, 0)

        friction = 0.1

        for body in self.bodies:
            positions.append(body.position)
            velocities.append(body.linearVelocity)
            avg_vel += velocities[-1]
            avg_pos += positions[-1]

            # body.ApplyForce(force=tuple(body.userData.force), point=(0,0), wake=False)

        avg_vel /= float(len(self.bodies))
        avg_pos /= float(len(self.bodies))

        # area = self._area()
        area = self.area

        force = 0
        if area > 0:
            force = self.softness * (self.rest_area / area - 1)

        force += self.softness * self.pressure / len(self.bodies)

        for i in range(len(self.bodies)):
            body = self.bodies[i]

            force_vector = (body.position - avg_pos)
            force_vector.Normalize()

            rel_vel = velocities[i] - avg_vel
            friction = rel_vel * self.damping

            # force_vector = body.userData['normal']
            force_vector *= force
            force_vector -= friction

            body.ApplyForce(force=(force_vector[0], force_vector[1]), point=(0,0), wake=False)

    # def _divide_joint(self, joint):
    #     joint.userData['divide'] = True

    #     self.nuke_joints.append(joint)
    #     joint.userData = None
    def divide_joint(self, joint):
        bodyA = joint.bodyA
        bodyB = joint.bodyB

        parents = joint_parents(joint)
        assert(self in parents)

        # New body
        body = self._create_body((bodyA.position + bodyB.position)/2)
        body.userData['parents'] = copy(parents)

        if self.verbose:
            print('Dividing joint', (bodyA.userData['id'], bodyB.userData['id']))
            print('\tadded body', body.userData['id'])

        for parent in parents:
            indexA = parent.bodies.index(bodyA)
            indexB = parent.bodies.index(bodyB)
            i, j = sorted((indexA, indexB))
            # index = max(indexA, indexB)

            if i == 0 and j == len(self.bodies)-1:
                self.bodies.append(body)
            else:
                parent.bodies.insert(j, body)

        self._create_joint(joint.bodyA, body, length=joint.length/2)
        self._create_joint(body, joint.bodyB, length=joint.length/2)


        self.world.DestroyJoint(joint)

    def grow(self, n):
        if self.interal_body:
            return

        self.pressure += n

        divide_joints = []
        for body in self.bodies:
            for jointEdge in body.joints:
                if self not in jointEdge.other.userData['parents']:
                    continue
                if jointEdge.joint.userData['type'] != 'outer_wall':
                    continue
                # print(jointEdge.joint.length, self.max_wall_length)
                joint = jointEdge.joint
                length = distance(joint.bodyA, joint.bodyB)

                if length > self.max_wall_length:
                    divide_joints.append(joint)

        if self.verbose and len(divide_joints):
            print("DIVIDE JOINTS", len(set(divide_joints)))

        for joint in set(divide_joints):
            self.divide_joint(joint)
        self.valid()

    def stress(self):
        return self._area() / self.rest_area

    def size(self):
        return self._area()

    def awake(self):
        return True

    def destroy(self):
        pass
        # for body in self.bodies:
        #     self.world.DestroyBody(body)
        #     body = None

    def joint_between(self, bodyA, bodyB):
        for jointEdge in bodyA.joints:
            if jointEdge.other == bodyB:
                return jointEdge.joint
        return None

    # def _get_joints(self):
        # joints = []
        # for joint in self.world.joints:
        #     if self in joint_parents(joint):
        #         joints.append(joint)
        # return joints

        # joints = []
        # for i in range(len(self.bodies)):
        #     joint = self.joint_between(self.bodies[i], self.bodies[i-1])
        #     joints.append(joint)
        # return joints

    def _angle(self):
        V, _ = pca(np.array([ b.position for b in self.bodies ]))
        return math.atan2(V[0][1], V[0][0])

    def step(self):
        self.area = self._area()
        self.center = self._center()
        self.angle = self._angle()
        self._computeDynamics()

    # Utility function used by divide to created nodes linkings two others.
    def _connect(self, bodyA, bodyB, k=1, n_joints=4):
        assert(bodyA in self.bodies)
        assert(bodyB in self.bodies)

        body_distance = distance(bodyA, bodyB)
        # if n_joints == None:
        # length = 3*self.wall_length
        # n_joints = math.floor(body_distance/length)
        length = body_distance / n_joints
        num_bodies = n_joints - 1

        # print('Connecting nodes')
        # print('\tdisance:',body_distance)
        # print('\tsegment_length:', length, length*num_bodies)

        new_bodies = []

        X = np.linspace(bodyB.position[0], bodyA.position[0], num_bodies+1, endpoint=False)[1:]
        Y = np.linspace(bodyB.position[1], bodyA.position[1], num_bodies+1, endpoint=False)[1:]
        assert(X.shape[0] == num_bodies)
        for pos in zip(X, Y):
            new_bodies.append(self._create_body(pos))

        joints = []

        joints.append(self._create_joint(bodyB, new_bodies[0], length =length, type='inner_wall'))
        joints.append(self._create_joint(new_bodies[-1], bodyA, length =length, type='inner_wall'))

        for i in range(0, num_bodies - 1):
            joints.append(self._create_joint(new_bodies[i], new_bodies[i+1], length =length, type='inner_wall'))

        return (new_bodies, [])

    def _axis_nodes(self, axis):
        """ Get the two nodes closest to axis ends """
        assert(axis == 0 or axis == 1)
        angle = self.angle + axis * (math.pi / 2)
        # angles = []
        self._update_body_angles()
        bodyA = min(
            self.bodies,
            key=lambda b: angular_distance(b.userData['angle'], angle))

        bodyB = min(
            self.bodies,
            key=lambda b: angular_distance(b.userData['angle'], bodyA.userData['angle']+pi))

        return (bodyA, bodyB)

    # Get the n closest elements to angle.
    def _spread(self, angle, n):
        if angle < 0:
            angle = 2*pi - abs(angle)
        # print('spread', angle)
        key = lambda b: angular_distance(b.userData['angle'], angle)
        return sorted(self.bodies, key=key)[:n]

    def contract(self, axis, n):
        if self.contracted_axis != None:
            for joint in self.inner_joints:
                joint.length *= .9
        else:
            self.contracted_axis = axis
            # elif self.contracted_axis == (not axis):
            #     return

            num_bodies = int(len(self.bodies)/4)

            angle = self.angle + ((1-axis)*pi/2)

            bodiesA = self._spread(angle, num_bodies)
            bodiesB = self._spread(angle+pi, num_bodies)

            # for bodyA, bodyB in zip(bodiesA, bodiesB):
            for bodyA in bodiesA+bodiesB:
                bodyB = self.cent_body
            #     joint = None
            #     for jointEdge in bodyA.joints:
            #         if jointEdge.other == bodyB:
            #             joint = jointEdge.joint
            #             joint.length *= .95
            #             break

                # No existing joint between.
                # if joint == None:
                joint = self._create_joint(bodyA, bodyB, hz=4, dr=.5)
                self.inner_joints.append(joint)

    def print_order(self):
        for body in self.bodies:
            # print(hex(id(body)), [id(j.other) for j in body.joints])
            print(body.userData['id'], [j.other.userData['id'] for j in body.joints])

    def _check_internal(self):
        self.interal_body = all(len(b.userData['parents']) != 1 for b in self.bodies)

    # TODO refactor this
    def divide(self, angle):
        # This model only divdes along primary and secondary axis.
        assert(angle == 0 or angle == math.pi/2)

        axis = int(bool(angle))

        if self.verbose:
            print('Dividing body', self)
            print('\taxis:', axis)
            print('\tstarting area:', self.area)
            print('\tstarting bodies:', len(self.bodies))

        # The points to split the cell
        bodyA, bodyB = self._axis_nodes(axis)
        i, j = (self.bodies.index(bodyA), self.bodies.index(bodyB))
        wall_bodies, _ = self._connect(bodyA, bodyB, k=1)

        if self.verbose:
            print('\ti,j:', i, j)
            print('\tbodyA,bodyB:', bodyA.userData['id'], bodyB.userData['id'])
            print('\twall bodies:', [b.userData['id'] for b in wall_bodies])


        if i > j:
            i,j = sorted((j, i))
            # Create new wall in middle.
            other_bodies = self.bodies[:i+1] + wall_bodies + self.bodies[j:]
            self.bodies  = self.bodies[i:j+1] + list(reversed(wall_bodies))
        else:
            # Create new wall in middle.
            other_bodies = self.bodies[:i+1] + list(reversed(wall_bodies)) + self.bodies[j:]
            self.bodies  = self.bodies[i:j+1] + wall_bodies

        # Create daughter and transfer bodies and joints
        daughter = SoftBody(self.world, position=None, bodies=other_bodies)

        daughter.rest_area = daughter._area()
        self.rest_area = self._area()

        daughter.pressure = 0#self.pressure/2
        self.pressure = 0

        for body in daughter.bodies:
            body.userData['parents'].remove(self)
            body.userData['parents'].add(daughter)

        for body in wall_bodies+[bodyA, bodyB]:
            body.userData['parents'].add(self)
            body.userData['parents'].add(daughter)

        self._create_inner_joints()
        self._check_internal()
        daughter._check_internal()

        if self.verbose:
            print('\tbodies', len(self.bodies), len(daughter.bodies))
            print('\trest areas', self.rest_area, daughter.rest_area)
            print()
        # print([b.userData['id'] for b in self.bodies])
        self.valid()
        daughter.valid()
        return daughter

    def _update_body_angles(self):
        center = self._center()
        for body in self.bodies:
            diff = body.position - center
            angle = math.atan2(diff[1], diff[0])
            if angle < 0:
                angle = 2*pi - abs(angle)
            assert(angle >= 0)
            assert(angle <= 2*math.pi)
            body.userData['angle'] = angle

    def valid(self):
        try:
            assert(self.area != None)
            assert(self.center != None)
            assert(self.angle != None)

            for i in range(len(self.bodies)):
                joint = self.joint_between(self.bodies[i], self.bodies[i-1])
                if joint == None:
                    for body in self.bodies:
                        body.angle = pi/2

                    self.bodies[i].angle = -pi/2
                    self.bodies[i-1].angle = -pi/2
                    print('jont is none', self.bodies[i].userData['id'], self.bodies[-1].userData['id'])

                assert(joint != None)

            for body in self.bodies:
                assert(self in body.userData['parents'])

        except AssertionError as e:
            print('!'*40)
            print('BODY IS NOT VALID!!', self)
            self.print_order()
            print('!'*40)

            raise AssertionError(e)

        # print(self, 'is valid')
        # assert(all([self in b.userData['parents'] for b in self.bodies]))
        # assert(all([self in j.userData['parents'] for j in self.joints]))
        # A = self._body_angles()
        # print(A)
        # assert(all(A[i] <= A[i+1] for i in range(len(A)-1)))
