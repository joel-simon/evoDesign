import time
from src.springs.Spring2D import World
from src.hexRenderer import HexPhysicsRenderer as Renderer
from src.hexmap import Map

class Simulation(object):
    def __init__(self):
        self.world = World()
        self.hmap = Map((8,8))

steps = 100
renderer = Renderer()
simulation = Simulation()



x = 0.
y = 100.
length = 10.
segments = 20

top = simulation.world.CreateStaticBody(position=(x, y))
bottom = simulation.world.CreateStaticBody(position=(x, y+length))

for i in range(1, segments):
    new_top = simulation.world.CreateDynamicBody(position=(x+i*length, y))
    new_bottom = simulation.world.CreateDynamicBody(position=(x+i*length, y+length))
    simulation.world.CreateDistanceJoint(top, new_top)
    simulation.world.CreateDistanceJoint(bottom, new_bottom)
    simulation.world.CreateDistanceJoint(new_top, new_bottom)
    simulation.world.CreateDistanceJoint(top, new_bottom)
    top = new_top
    bottom = new_bottom


t0 = time.time()
for i in range(100):
    simulation.world.step()
    # renderer.render(simulation)
# for body in simulation.world.bodies:
#     print body.position
# for joint in simulation.world.joints:
#     print(joint.bodyA.position, joint.bodyB.position)

print('complete', time.time() - t0)

renderer.hold()
