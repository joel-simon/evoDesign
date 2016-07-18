import math
import random
import time
from Box2D import *

SQRT3 = math.sqrt( 3 )
def hex_points(x, y, radius):
    hex_coords = [( .5 * radius, 0 ),
        ( 1.5 * radius, 0 ),
        ( 2 * radius, SQRT3 / 2 * radius ),
        ( 1.5 * radius, SQRT3 * radius ),
        ( .5 * radius, SQRT3 * radius ),
        ( 0, SQRT3 / 2 * radius ),
        ( .5 * radius, 0 )
    ]
    return [((x + _x), ( y + _y)) for ( _x, _y ) in hex_coords]

class HexBody(object):
    """docstring for RigidBody"""
    def __init__(self, world, position, radius, neighbors, static=[]):
        self.bodies = dict()
        self.world = world
        self.radius = radius
        self.position = position

        hex_coords = [
            ( .5 * radius, 0 ), # bl
            ( 1.5 * radius, 0 ), # br
            ( 2 * radius, SQRT3 / 2 * radius ), # right
            ( 1.5 * radius, SQRT3 * radius ),
            ( .5 * radius, SQRT3 * radius ),
            ( 0, SQRT3 / 2 * radius ),
            ( .5 * radius, 0 )
        ]
        positions = {
            'top_left': (-.5 * radius+position[0], SQRT3 * radius /2+position[1]),
            'top_right': (.5 * radius+position[0], SQRT3 * radius /2+position[1]),
            'right': ( radius+position[0], 0 +position[1]),
            'bottom_right': (.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1]),
            'bottom_left': (-.5 * radius+position[0], -1 * SQRT3 * radius /2+position[1]),
            'left': ( -radius+position[0], 0 +position[1]),
        }
        self.userData = dict()
        self.nuke_bodies = []


        for direction, neighbor in neighbors.items():
            if direction == 'top':
                if neighbor:
                    self.bodies['top_left'] = neighbor.bodies['bottom_left']
                    self.bodies['top_right'] = neighbor.bodies['bottom_right']

            elif direction == 'top_right':
                if neighbor:
                    self.bodies['top_right'] = neighbor.bodies['left']
                    self.bodies['right'] = neighbor.bodies['bottom_left']

            elif direction == 'bottom_right':
                if neighbor:
                    self.bodies['right'] = neighbor.bodies['top_left']
                    self.bodies['bottom_right'] = neighbor.bodies['left']

            elif direction == 'bottom':
                if neighbor:
                    self.bodies['bottom_right'] = neighbor.bodies['top_right']
                    self.bodies['bottom_left'] = neighbor.bodies['top_left']

            elif direction == 'bottom_left':
                if neighbor:
                    self.bodies['left'] = neighbor.bodies['top_right']
                    self.bodies['bottom_left'] = neighbor.bodies['right']

            elif direction == 'top_left':
                if neighbor:
                    self.bodies['left'] = neighbor.bodies['bottom_right']
                    self.bodies['top_left'] = neighbor.bodies['right']

            else:
                print(direction)
                assert(False)

        for derp in positions.keys():
            if derp not in self.bodies:
                is_static = derp in static
                self.bodies[derp] = self.create_body(positions[derp], is_static)


        assert(len(set(self.bodies.keys())) == 6)

        for body in self.bodies.values():
            body.userData['parents'].add(self)

        self.create_joint(self.bodies['top_left'], self.bodies['top_right'])
        self.create_joint(self.bodies['top_right'], self.bodies['right'])
        self.create_joint(self.bodies['right'], self.bodies['bottom_right'])
        self.create_joint(self.bodies['bottom_right'], self.bodies['bottom_left'])
        self.create_joint(self.bodies['bottom_left'], self.bodies['left'])
        self.create_joint(self.bodies['left'], self.bodies['top_left'])

        a = self.create_joint(self.bodies['top_left'], self.bodies['bottom_left'], hz=0)
        b = self.create_joint(self.bodies['top_left'], self.bodies['bottom_right'], hz=0)
        c = self.create_joint(self.bodies['bottom_right'], self.bodies['top_right'], hz=0)

        self.inner_joints = [a, b, c]
        # self.create_joint(self.bodies['top_right'], self.bodies['bottom_left'], hz=0)

        # self.create_joint(self.bodies['left'], self.bodies['right'], hz=0)

    def create_body(self, position, static):
        body_params = {
            'position': position,
            'fixedRotation': True,
            'linearDamping': 0,
            'userData': { 'origin': position, 'parents': set([self]) }
        }
        if static:
            body = self.world.CreateStaticBody(**body_params)
        else:
            body = self.world.CreateDynamicBody(**body_params)
        body.CreateCircleFixture(
            shape=b2CircleShape(radius=self.radius/8),
            density=0,
            friction=0
        )
        body.mass = 0
        return body

    def destroy(self):
        for joint in self.inner_joints:
            self.world.DestroyJoint(joint)

        for body in self.bodies.values():
            body.userData['parents'].remove(self)
            if len(body.userData['parents']) == 0:
                self.world.DestroyBody(body)

    def create_joint(self, bodyA, bodyB, hz=0, dr=.9):
        joint = self.world.CreateDistanceJoint(
            frequencyHz=hz,
            dampingRatio=dr,
            bodyA=bodyA,
            bodyB=bodyB,
            localAnchorA=(0,0),
            localAnchorB=(0,0),
            collideConnected=False,
            # userData = {
            #     'type': type,
            #     # 'parents': set([self]),
            # },
        )
        return joint
