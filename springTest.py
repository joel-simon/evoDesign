import time
from src.springs.Spring2D import World
from src.hexmap import Map
import pygame
import os

class Renderer(object):
    """draw the spring world"""
    def __init__(self, save=None):
        self.scale = 3
        pygame.init()
        self.font = pygame.font.SysFont("monospace", 18)
        self.screen = pygame.display.set_mode((800, 800))

    def screen_xy(self, xy):
        return (int(self.scale*xy[0])+20, int(800 - self.scale*xy[1]))

    def draw_joint(self, joint, color = (10, 10, 10)):
        x1, y1 = self.screen_xy(joint.bodyA.position)
        x2, y2 = self.screen_xy(joint.bodyB.position)
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2))

    def draw_body(self, body):
        x, y = self.screen_xy(body.position)
        radius = 2#max(int(body.fixtures[0].shape.radius), 2)
        pygame.draw.circle(self.screen, (10, 10, 10), (x, y), radius)

    def render(self, world):
        bodies = world.bodies
        joints = world.joints

        self.screen.fill((255,255,255))

        num_bodies = self.font.render("# bodies: %i" % len(bodies),1,(0,0,0) )
        self.screen.blit(num_bodies, (10,50))

        for body in bodies:
            self.draw_body(body)

        for joint in joints:
            force = joint.GetReactionForce()
            color_diff = int(force * 512)
            color_diff = min(127, max(0, color_diff))
            color = (128+color_diff, 128-color_diff, 128-color_diff)
            self.draw_joint(joint, color)

        pygame.display.flip()

    def hold(self):
        while True:
            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                sys.exit()

renderer = Renderer()

def beam():
    world = World(resolve_steps=100, gravity=-10)
    x = 0.
    y = 100.
    length = 10.
    segments = 20
    steps = 100

    top = world.CreateStaticBody(x=x, y=y)
    bottom = world.CreateStaticBody(x=x, y=y+length)

    for i in range(1, segments):
        new_top = world.CreateDynamicBody(x=x+i*length, y=y)
        new_bottom = world.CreateDynamicBody(x=x+i*length, y=y+length)
        world.CreateDistanceJoint(top, new_top)
        world.CreateDistanceJoint(bottom, new_bottom)
        world.CreateDistanceJoint(new_top, new_bottom)
        world.CreateDistanceJoint(top, new_bottom)
        top = new_top
        bottom = new_bottom

    t0 = time.time()
    for i in range(steps):
        if i%10 == 0:
            print(i)
        world.step()
        renderer.render(world)
        time.sleep(.05)

    print('complete', time.time() - t0)

def grid():
    rows = 10
    cols = 10
    length = 10
    steps = 100
    bodies = []

    for row in range(rows):
        body_row = []
        for col in range(cols):
            x = col * length
            y = row * length
            
            if row == 0:
                body_row.append(world.CreateStaticBody(x=x, y=y))
                if col > 1:
                    world.CreateDistanceJoint(body_row[-2], body_row[-1])
            else:
                body = world.CreateDynamicBody(x=x, y=y)
                body_row.append(body)
                world.CreateDistanceJoint(body, bodies[-1][col])
                if col > 0:
                    world.CreateDistanceJoint(body, body_row[-2])

        bodies.append(body_row)

    t0 = time.time()
    for i in range(steps):
        if i%10 == 0:
            print(i)
        world.step()
        renderer.render(world)
        time.sleep(.5)

    print('complete', time.time() - t0)

beam()
