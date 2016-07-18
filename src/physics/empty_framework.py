from time import time

from Box2D import (b2World, b2AABB, b2CircleShape, b2Color, b2Vec2)
from Box2D import (b2ContactListener, b2DestructionListener, b2DrawExtended)
from Box2D import (b2Fixture, b2FixtureDef, b2Joint)
from Box2D import (b2GetPointStates, b2QueryCallback, b2Random)
from Box2D import (b2_addState, b2_dynamicBody, b2_epsilon, b2_persistState)

from .settings import fwSettings


class fwDestructionListener(b2DestructionListener):
    """
    The destruction listener callback:
    "SayGoodbye" is called when a joint or shape is deleted.
    """

    def __init__(self, test, **kwargs):
        super(fwDestructionListener, self).__init__(**kwargs)
        self.test = test

    def SayGoodbye(self, obj):
        if isinstance(obj, b2Joint):
            if self.test.mouseJoint == obj:
                self.test.mouseJoint = None
            else:
                self.test.JointDestroyed(obj)
        elif isinstance(obj, b2Fixture):
            self.test.FixtureDestroyed(obj)


class Framework(b2ContactListener):
    def __reset(self):
        """ Reset all of the variables to their starting values.
        Not to be called except at initialization."""
        # Box2D-related
        self.points = []
        self.world = None
        self.settings = fwSettings
        self.using_contacts = False
        self.stepCount = 0

        # Box2D-callbacks
        self.destructionListener = None

    def __init__(self):
        super(Framework, self).__init__()

        self.__reset()

        # Box2D Initialization
        self.world = b2World(gravity=(0, -10), doSleep=True)

        # self.destructionListener = fwDestructionListener(test=self)
        # self.world.destructionListener = self.destructionListener
        self.world.contactListener = self
        # self.t_steps, self.t_draws = [], []

    def __del__(self):
        pass

    def run(self, steps=None):
        self.stepCount = 0
        for i in range(steps):
            self.Step(self.settings)

    def Step(self, settings):
        self.stepCount += 1
        # Don't do anything if the setting's Hz are <= 0
        if settings.hz > 0.0:
            timeStep = 1.0 / settings.hz
        else:
            timeStep = 0.0

        # Set the other settings that aren't contained in the flags
        self.world.warmStarting = settings.enableWarmStarting
        self.world.continuousPhysics = settings.enableContinuous
        self.world.subStepping = settings.enableSubStepping

        # Reset the collision points
        self.points = []

        # Tell Box2D to step
        t_step = time()
        self.world.Step(timeStep, settings.velocityIterations,
                        settings.positionIterations)
        self.world.ClearForces()
        t_step = time() - t_step

        # Update the debug draw settings so that the vertices will be properly
        # converted to screen coordinates
        t_draw = time()


        # Take care of additional drawing (fps, mouse joint, slingshot bomb,
        # contact points)

    def PreSolve(self, contact, old_manifold):
        """
        This is a critical function when there are many contacts in the world.
        It should be optimized as much as possible.
        """
        if not (self.settings.drawContactPoints or
                self.settings.drawContactNormals or self.using_contacts):
            return
        elif len(self.points) > self.settings.maxContactPoints:
            return

        manifold = contact.manifold
        if manifold.pointCount == 0:
            return

        state1, state2 = b2GetPointStates(old_manifold, manifold)
        if not state2:
            return

        worldManifold = contact.worldManifold

        # TODO: find some way to speed all of this up.
        self.points.extend([dict(fixtureA=contact.fixtureA,
                                 fixtureB=contact.fixtureB,
                                 position=worldManifold.points[i],
                                 normal=worldManifold.normal.copy(),
                                 state=state2[i],
                                 )
                            for i, point in enumerate(state2)])
