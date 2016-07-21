import pygame
import pygame.gfxdraw
from collections import defaultdict
SQRT3 = 1.73050808
pygame.init()
font = pygame.font.SysFont("monospace", 14)
screen = pygame.display.set_mode((615, 800))

w, h = screen.get_size()
radius = 10
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
    return [((x + left), ( y + top)) for ( x, y ) in hex_coords]

def draw_hex_map(grid):
    screen.fill((255,255,255))

    values = []
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            values.append(grid[row][col])

    min_v = min(values)
    max_v = max(values)

    assert(min_v != max_v)

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            v = grid[row][col]

            if max_v > 0:
                scaled = (v - min_v) / (max_v - min_v)
            else:
                scaled = 0
            color = (200, 10, 10, (scaled) * 255)

            points = hex_points(row, col, radius)
            for i, xy in enumerate(points):
                points[i] = xy_to_screen(xy)

            pygame.gfxdraw.filled_polygon(screen, points, color)
            pygame.gfxdraw.aapolygon(screen, points, (20, 20, 20, 100))

    screen.blit(font.render("min %f"%(min_v), True, (0,0,0)), (10, 20))
    screen.blit(font.render("max %f"%(max_v), True, (0,0,0)), (10, 40))
    screen.blit(font.render("dif %f"%(max_v- min_v), True, (0,0,0)), (10, 60))

    pygame.display.flip()
