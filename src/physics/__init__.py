class PhysicsBody(object):
    """docstring for PhysicsBody"""
    def __init__(self, world, position, shape, density, friction):
        self.world = world
        self.position = position
        self.shape = shape
        self.density = density
        self.friction = friction

        self.bodies = []
        self.joints = []

    def grow(self):
        raise NotImplementedError

    def get_stress(self):
        raise NotImplementedError

    def neighbors(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError
