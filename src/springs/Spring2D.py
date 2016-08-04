from .vector import Vect2D as Vect

class World(object):
    """docstring for World"""
    def __init__(self):
        self.joints = []
        self.bodies = []
        self.gravity = Vect(0, -2)

    def CreateStaticBody(self, **kwargs):
        p = kwargs['position']
        self.bodies.append(StaticBody(p[0], p[1]))
        return self.bodies[-1]

    def CreateDynamicBody(self, **kwargs):
        p = kwargs['position']
        self.bodies.append(Body(p[0], p[1]))
        return self.bodies[-1]

    def CreateDistanceJoint(self, bodyA, bodyB, **kwargs):
        joint = Joint(bodyA, bodyB)
        self.joints.append(joint)
        bodyA.joints.append(joint)
        bodyB.joints.append(joint)
        return self.joints[-1]

    def DestroyBody(self, body):
        self.bodies.remove(body)
        return

    def DestroyJoint(self, joint):
        joint.bodyA.joints.remove(joint)
        joint.bodyB.joints.remove(joint)
        self.bodies.remove(joint)
        return

    def step(self):
        steps = 1000
        delta = 1.0 / steps

        for j in range(steps):
            for joint in self.joints:
                joint.resolve()

            for body in self.bodies:
                body.accelerate(self.gravity)
                body.simulate(delta)

class Body(object):
    """docstring for Body"""
    def __init__(self, x, y, userData={}):
        self.position = Vect(x, y)
        self.previous = Vect(x, y)
        self.acceleration = Vect(0., 0.)
        self.userData = userData
        self.mass = 1
        self.joints = []

    def accelerate(self, vect):
        self.acceleration.iadd(vect)

    def correct(self, vect):
        self.position.iadd(vect)

    def simulate(self, delta):
        self.acceleration.imul(delta*delta)
        position = self.position.mul(2.).sub(self.previous).add(self.acceleration)
        self.previous = self.position
        self.position = position
        self.acceleration.zero()


class StaticBody(Body):
    def accelerate(self, vect):
        pass
    def correct(self, vect):
        pass
    def simulate(self, delta):
        pass


class Joint(object):
    """docstring for Joint"""
    def __init__(self, bodyA, bodyB, userData={}):
        assert(isinstance(bodyA, Body))
        assert(isinstance(bodyB, Body))
        assert(bodyA != bodyB)
        self.bodyA = bodyA
        self.bodyB = bodyB
        self.target = bodyA.position.distance(bodyB.position)
        self.userData = userData

    def resolve(self):
        pos1 = self.bodyA.position
        pos2 = self.bodyB.position
        direction = pos2.sub(pos1)
        length = direction.length()
        factor = (length-self.target)/(length*2.1)
        correction = direction.mul(factor)

        self.bodyA.correct(correction)
        correction.imul(-1)
        self.bodyB.correct(correction)

    def GetReactionForce(self, i):
        return Vect(0,0)
