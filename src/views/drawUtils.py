import pygame
pygame.font.init()
myfont = pygame.font.SysFont("monospace", 20)

BLACK = (0,0,0)
WHITE = (255,255,255)

margin = 2

def xy_to_screen(x, y, surface):
    w, h = surface.get_size()
    return (int(x+margin), int(h-y-margin))

def draw_polygon(surface, points, color, t=0):
    pygame.draw.polygon(surface, color, points, t)

def draw_circle(surface, position, radius, color):
    pygame.draw.circle(surface, color, position, radius)

def draw_line(surface, positionA, positionB, color, width=1):
    pygame.draw.line(surface, color, positionA, positionB, width)

def draw_rect(surface, rect, color, width=1):
    pygame.draw.rect(surface, color, rect, width)

def draw_text(surface, position, string, color=BLACK):
    assert(len(position) == 2)
    assert(isinstance(string, str))
    label = myfont.render(string, 1, BLACK)
    surface.blit(label, position)

def rgb_int(c):
    return tuple((min(255, max(0, int(c_*255))) for c_ in c))
    # return (int(c[0]*255), int(c[1]*255), int(c[2]*255))

# print rgb_int((.5, .5, 2))
