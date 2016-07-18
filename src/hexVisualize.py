import time
import pygame
import pygame.gfxdraw

pygame.init()
font = pygame.font.SysFont("monospace", 18)
screen = pygame.display.set_mode((800, 800))

# from box2DPhysics import Box2DPhysics
# from physics import VoronoiSpringPhysics
from os.path import join
import sys
import os
import subprocess
import argparse

BLACK = (0,0,0)
LIGHT_GREEN = (0, 200, 0, 10)

class HexRenderer(object):
    """docstring for HexRenderer"""
    def __init__(self, simulation):
        self.simulation = simulation
        self.scale = 3

    def screen_xy(self, xy):
        return (int(self.scale*xy[0])+20, int(800 - self.scale*xy[1]))

    def draw_joint(self, joint, color = (10, 10, 10)):
        x1, y1 = self.screen_xy(joint.bodyA.position)
        x2, y2 = self.screen_xy(joint.bodyB.position)
        pygame.gfxdraw.line(screen, x1, y1, x2, y2, color)

    def draw_body(self, body):
        x, y = self.screen_xy(body.position)
        # print(body.fixtures[0])
        radius = int(body.fixtures[0].shape.radius)
        pygame.gfxdraw.aacircle(screen, x, y, radius, (10, 10, 10))

        # a = node.morphogen_concentrations[0][0]
        # red = int(200 * (a-m_range[0])/(1+m_range[1]-m_range[0]))
        # pygame.gfxdraw.filled_circle(screen, x, y, int(node.r), (200, 10, 10, red))

    def render(self):
        print('render')
        bodies = self.simulation.world.bodies
        joints = self.simulation.world.joints

        print(len(bodies))
        print(len(joints))
        # sim_r = simulation.hex_radius
        # sim_max_x

        screen.fill((255,255,255))

        # c_a = [ n.morphogen_concentrations[0][0] for n in bodies ]
        # c_b = [ n.morphogen_concentrations[0][1] for n in bodies ]

        # max_stress = max(n.get_stress() for n in bodies)

        # m_range = (min(c_a), max(c_a))

        # mintext = font.render("a range:(%f, %f)" % (min(c_a), max(c_a)),1,(0,0,0) )
        # screen.blit(mintext, (10,10))

        # mintext = font.render("b range:(%f, %f)" % (min(c_b), max(c_b)),1,(0,0,0) )
        # screen.blit(mintext, (10,30))

        num_bodies = font.render("# bodies: %i" % len(bodies),1,(0,0,0) )
        screen.blit(num_bodies, (10,50))

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

        # V, variance = pca(np.array(points))
        # v = V[0]
        # x1, y1, = 400,400
        # x2 = int(400+50*v[0])
        # y2 = 800 - int(400+50*v[1])
        # pygame.draw.line(screen, (10,10,10), (x1, y1), (x2, y2), 5)

        pygame.display.flip()


    def hold(self):
        while True:
            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                sys.exit()
