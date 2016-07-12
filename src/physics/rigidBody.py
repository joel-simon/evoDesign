from . import PhysicsBody
from Box2D import *
import math
class RigidBody(PhysicsBody):
    """docstring for RigidBody"""
    def __init__(self, world, position, shape, density, friction, damping):
        super(RigidBody, self).__init__(world, position, shape, density, friction, damping)

        self.body = self.world.CreateDynamicBody(
          position=self.position,
          fixedRotation=True,
          userData={'name': 'node', 'parent': self},
          linearDamping=self.damping,
          # angularDamping=9999,
        )

        # No internal joints
        self.joints = None
        self.bodies.append(self.body)
        self.update_shape()
        self.sensor_shape = 2 # size multiplier, >1

    def update_shape(self):
        if len(self.body.fixtures) == 1:
            self.body.DestroyFixture(self.body.fixtures[0])

        # Circle
        if len(self.shape) == 1:
            # self.body.CreateCircleFixture(
            #     shape=b2CircleShape(radius=self.shape[0]*self.sensor_shape),
            #     sensor=True
            # )

            self.body.CreateCircleFixture(
                shape=b2CircleShape(radius=self.shape[0]),
                density=self.density, friction=self.friction
            )

        # Rectangle
        else:
            self.body.CreatePolygonFixture(
                box=self.shape,
                density=density, friction=friction
            )

    def grow(self, X):
        self.shape[0] += X[0]
        self.update_shape()

    def neighbors(self):
        pass

    def step(self):
        pass

    def divide(self, angle):
        r_old = self.shape[0]
        # 2(pi * r_old*r_old) = pi * r_new*r_new
        self.shape[0] = math.sqrt(r_old*r_old /2)


        self.update_shape()

        r_move = r_old - self.shape[0]
        diff = (math.cos(angle)*r_move, math.sin(angle)*r_move)

        daughter_position = (self.body.position[0] + diff[0],self.body.position[1] + diff[1])
        daughter = RigidBody(world=self.world,
                            position=daughter_position,
                            shape=self.shape,
                            density=self.density,
                            friction=self.friction,
                            damping=self.damping)

        self.body.position -= diff

        return daughter
        # fixt = self.body.fixtures[0]
        # oldw = 2*abs(fixt.shape.vertices[0][0])
        # oldh = 2*abs(fixt.shape.vertices[0][1])

        # axis = 0
        # if oldh > oldw:
        #   axis = 1

        # angle   = body.angle - (math.radians(90) * (axis))
        # angvect = b2Vec2(math.cos(angle), math.sin(angle))

        # w = oldw
        # h = oldh

        # if axis == 0:
        #   w/=2
        # else:
        #   h/=2

        # self.set_size(body, w, h)
        # daughter = self.add_body(body.position[0], body.position[1], [w, h])
        # daughter.angle = body.angle

        # if axis == 1:
        #   body.position -= angvect * (oldh/4)
        #   daughter.position += angvect * (oldh/4)
        # else:
        #   body.position -= angvect * (oldw/4)
        #   daughter.position += angvect * (oldw/4)

        # self.add_edge(body, daughter)
        # return daughter

    def add_edge(self, other):
        for jointEdge in self.body.joints:
            if jointEdge.other == other.body:
                return
        diff = self.body.position-other.body.position
        angle = math.atan2(diff[1], diff[0])
        # p_angle = angle+ math.pi/2#(-angle[1], angle[0])

        # r = self.shape[0]
        # r_o = other.shape[0]

        # r = self.shape[0] + other.shape[0]

        DJ = self.world.CreateJoint(b2DistanceJointDef(
            bodyA=self.body,
            bodyB=other.body,
            localAnchorA=(0,0),#(math.cos(p_angle)*r, math.sin(p_angle)*r),
            localAnchorB=(0,0),#(-math.cos(p_angle)*r_o, -math.sin(p_angle)*r_o),
            collideConnected=True,
            length=(self.shape[0]+other.shape[0])
        ))
        # joint = self.world.CreateJoint(b2DistanceJointDef(
        #     bodyA=self.body,
        #     bodyB=other.body,
        #     localAnchorA=(-math.cos(p_angle)*r, -math.sin(p_angle)*r),
        #     localAnchorB=(math.cos(p_angle)*r_o, math.sin(p_angle)*r_o),
        #     collideConnected=True,
        #     # maxLength=(self.shape[0]+other.shape[0]) *.95
        # ))

        # PJ = self.world.CreatePrismaticJoint(
        #     bodyA=self.body,
        #     bodyB=other.body,
        #     anchor=self.body.worldCenter,
        #     # referenceAngle=0,
        #     # axis=(1, 1),
        #     axis=(math.cos(angle), math.sin(angle)),
        #     # lowerTranslation=-2,
        #     # upperTranslation=2,
        #     # enableLimit=True,
        #     # motorForce=1.0,
        #     # motorSpeed=0.0,
        #     # enableMotor=False,
        #     collideConnected=True,
        # )
        return (DJ,)

        # joint = self.world.CreateJoint(b2RopeJointDef(
        #     bodyA=self.body,
        #     bodyB=other.body,
        #     localAnchorA=(0,0),
        #     localAnchorB=(0,0),
        #     collideConnected=True,
        #     maxLength=(self.shape[0]+other.shape[0]) *.95
        # ))
        # diff = self.body.position-other.body.position
        # angle = math.atan2(diff[1], diff[0])
        # r = self.shape[0] + other.shape[0]
        # anchor = (math.cos(angle)*r, math.sin(angle)*r)

        # joint = self.world.CreateJoint(b2WeldJointDef(
        #     bodyA=self.body,
        #     bodyB=other.body,
        #     anchor=(self.body.position+other.body.position)/2,
        #     collideConnected=True,
        #     frequencyHz=1.0,
        #     dampingRatio=0.5,
        # ))
        # return joint
