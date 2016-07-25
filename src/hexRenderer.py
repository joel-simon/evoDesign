import time
import pygame
# import pygame.gfxdraw

# from box2DPhysics import Box2DPhysics
# from physics import VoronoiSpringPhysics
from os.path import join
import sys
import os
import subprocess
import argparse

BLACK = (0,0,0)
LIGHT_GREEN = (0, 200, 0, 10)

class HexPhysicsRenderer(object):
    """docstring for HexRenderer"""
    def __init__(self):
        self.scale = 3
        pygame.init()
        self.font = pygame.font.SysFont("monospace", 18)
        self.screen = pygame.display.set_mode((800, 800))

    def screen_xy(self, xy):
        return (int(self.scale*xy[0])+20, int(800 - self.scale*xy[1]))

    def draw_joint(self, joint, color = (10, 10, 10)):
        x1, y1 = self.screen_xy(joint.bodyA.position)
        x2, y2 = self.screen_xy(joint.bodyB.position)
        # pygame.gfxdraw.line(self.screen, x1, y1, x2, y2, color)
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2))

    def draw_body(self, body):
        x, y = self.screen_xy(body.position)
        radius = max(int(body.fixtures[0].shape.radius), 2)
        # pygame.gfxdraw.aacircle(self.screen, x, y, radius, (10, 10, 10))
        pygame.draw.circle(self.screen, (10, 10, 10), (x, y), radius)

    def render(self, simulation):
        bodies = simulation.world.bodies
        joints = simulation.world.joints

        self.screen.fill((255,255,255))

        num_bodies = self.font.render("# bodies: %i" % len(bodies),1,(0,0,0) )
        self.screen.blit(num_bodies, (10,50))

        for body in bodies:
            self.draw_body(body)

        if len(joints):
            max_force = max(j.GetReactionForce(.60).Normalize() for j in joints)
            for joint in joints:
                force = joint.GetReactionForce(.60).Normalize()
                if max_force == 0:
                    color = (0, 10, 10)
                else:
                    color = (int(255*force/max_force), 10, 10)
                self.draw_joint(joint, color)

        pygame.display.flip()


    def hold(self):
        while True:
            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                sys.exit()

SQRT3 = 1.73050808
pygame.init()
font = pygame.font.SysFont("monospace", 14)
screen = pygame.display.set_mode((615, 800))

w, h = screen.get_size()
radius = 15
margin = 3


def xy_to_screen(xy):
    return (xy[0]+margin, h-xy[1]-margin)

def hex_points(row, col, radius):
    offset = radius * SQRT3 / 2 if col % 2 else 0
    top    = offset + SQRT3 * row * radius
    left    = 1.5 * col * radius

    hex_coords = [( .5 * radius, 0 ),
        ( 1.5 * radius, 0 ),
        ( 2 * radius, SQRT3 / 2 * radius ),
        ( 1.5 * radius, SQRT3 * radius ),
        ( .5 * radius, SQRT3 * radius ),
        ( 0, SQRT3 / 2 * radius ),
        ( .5 * radius, 0 )
    ]
    return [(int(x + left), int( y + top)) for ( x, y ) in hex_coords]


class HexRenderer(object):
    """docstring for HexRenderer"""
    def __init__(self, save=None):
        self.save = save
        self.frame = 0

    def render(self, simulation):
        C = simulation.hmap
        A = simulation.A
        rows, cols = simulation.bounds

        screen.fill((255,255,255))

        values = []
        for row in range(rows):
            for col in range(cols):
                values.append(A[0][row][col])

        min_a = min(values)
        max_a = max(values)

        for row in range(rows):
            for col in range(cols):
                v = C[row][col]
                a = A[0][row][col]

                scaled = (min(a,30) / 30.)
                # if max_a > 0:
                #     scaled = (a - min_a) / (max_a - min_a)
                # else:
                #     scaled = 0

                points = hex_points(row, col, radius)
                for i, xy in enumerate(points):
                    points[i] = xy_to_screen(xy)


                color = (int(scaled * 255), 100, 100)
                pygame.draw.polygon(screen, color, points)

                if v:
                    pygame.draw.polygon(screen, (10,200,10), points, 5)
                # pygame.draw.polygon(screen, (20, 20, 20),points,  1)

        screen.blit(font.render("min %f"%(min_a), True, (0,0,0)), (10, 20))
        screen.blit(font.render("max %f"%(max_a), True, (0,0,0)), (10, 40))
        screen.blit(font.render("dif %f"%(max_a- min_a), True, (0,0,0)), (10, 60))

        pygame.display.flip()

        if self.save:
            name = '%d.jpg' % self.frame
            pygame.image.save(screen, os.path.join(self.save, name))
        self.frame += 1

    def hold(self):
        while True:
            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                sys.exit()

