class PhysicsBody(object):
    """docstring for PhysicsBody"""
    def __init__(self, world, position, shape, density, friction, damping):
        self.world = world
        # self.id = ID
        self.position = position
        self.shape = shape
        self.density = density
        self.friction = friction
        self.damping = damping

        self.userData = {}
        self.bodies = []
        # self.joints = []
        self.nuke_joints = []

    def grow(self):
        raise NotImplementedError

    def get_stress(self):
        raise NotImplementedError

    def neighbors(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

class PhysicsSystem(object):
    """docstring for PhysicsSystem"""
    def __init__(self, arg):
        self.physics_bodies = []

    def run(self):
        raise NotImplementedError

    def finished(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def grow_body(self, body, n):
        body.grow(n)

    def destroy_body(self, body):
        raise NotImplementedError

    def divide_body(self, body, angle):
        raise NotImplementedError

    def create_body(self, body):
        raise NotImplementedError

    def neighbors(self, body):
        raise NotImplementedError


