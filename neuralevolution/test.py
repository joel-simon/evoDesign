import pygame, math, sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(linewidth=125, precision=2, suppress=True)

from hexmap import Map, draw_map

pygame.init()
size      = width, height = 640, 640
screen    = pygame.display.set_mode(size)
basicFont = pygame.font.SysFont(None, 24)
BLACK     = (0,0,0)
WHITE     = (255, 255, 255)

size = width, height = 320, 240

m = Map(8, 8)
m.values[3, 3] = 1

print(m.ascii())
screen.fill( WHITE)
draw_map(screen, m, 30)    
pygame.display.update()

while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()