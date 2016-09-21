import os, sys
import pygame
from .drawUtils import draw_rect

BLACK = (0,0,0)
WHITE = (255,255,255)

class View(object):
    """docstring for View"""
    def __init__(self, w, h, simulation, save=False):
        self.w = w
        self.h = h
        self.save = save

        self.screen = pygame.display.set_mode((w, h))

        self.simulation = simulation
        self.mod_sims = [m for m in simulation.module_simulations if m.has_render]
        # print simulation.module_simulations[0].has_render

        self.x_divisions = 2
        self.y_divisions = 2
        self.division_width = int(self.w / float(self.x_divisions))
        self.division_height = int(self.h / float(self.y_divisions))

        self.surfaces = []

        self.frame = 0

        dw, dh = self.division_width, self.division_height
        for y_i in range(self.y_divisions):
            for x_i in range(self.x_divisions):
                d = (x_i*dw, y_i*dh, dw, dh)
                ss = self.screen.subsurface(d)
                self.surfaces.append(ss)

    def render(self):
        self.screen.fill(WHITE)

        self.simulation.render(self.surfaces[0])

        for mod_sim, surface in zip(self.mod_sims, self.surfaces[1:]):
            mod_sim.render(surface)

        # Draw borders.
        for surface in self.surfaces:
            w, h = surface.get_size()
            rect = (-1, -1, self.w+1, self.h+1)
            draw_rect(surface, rect, BLACK, 2)

        pygame.display.flip()

        if self.save:
            path = os.path.join(self.save, '%d.jpg' % self.frame)
            pygame.image.save(self.screen, path)

        self.frame += 1

    def hold(self):
        while True:
            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                sys.exit()

