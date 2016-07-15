import os
import sys
import math
from src.hexmap import Map

import pygame
import pygame.gfxdraw
from collections import defaultdict

pygame.init()
font = pygame.font.SysFont("monospace", 14)
screen = pygame.display.set_mode((800, 800))
margin = 3
w, h = screen.get_size()
radius = 50

BLACK = (0,0,0)
GREY  = (50, 50, 50)
WHITE = (255, 255, 255)
RED   = (200, 0, 0)
GREEN = (0, 200, 0)
SQRT3 = math.sqrt( 3 )

class Node(object):
    """docstring for Node"""
    def __init__(self):
        # self.depth = 0
        self.force_left = 0
        self.force_center = 1
        self.force_right = 0
        self.open = False

    def __str__(self):
        if self.open:
            return ('%.1f %.1f %.1f' %(self.force_left, self.force_center, self.force_right))
        else:
            return ('%.1f %.1f %.1f' %(self.force_left, self.force_center, self.force_right))

def hex_points(row, col, radius, screen_height):
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

def draw_string(xy, str, color=(0,0,0, 255)):
    screen.blit(font.render(str, True, color), xy)

def xy_to_screen(xy):
    return (xy[0]+margin, h-xy[1]-margin)

def draw_hex_map(screen, hexmap, start = (0,0)):

    for col in range(hexmap.cols):
        for row in range(hexmap.rows):
            cell = hexmap.values[row][col]

            points = hex_points(row, col, radius, h)
            for i, xy in enumerate(points):
                points[i] = xy_to_screen(xy)

            if cell == -1:
                pygame.draw.polygon(screen, BLACK, points)

            elif cell != 0:
                if cell.open:
                    pygame.draw.polygon(screen, GREEN, points)
                else:
                    pygame.draw.polygon(screen, RED, points)

                offset = radius * SQRT3 / 2 if col % 2 else 0
                top    = offset + SQRT3 * row * radius
                left    = 1.5 * col * radius

                string = str(cell)
                draw_string(xy_to_screen((left+3, top+radius)), string)

            pygame.draw.polygon(screen, GREY, points, 1)
    return

def calculate_depth(hmap):
    seen = set()
    opens = set((0, c) for c in range(hmap.cols) if hmap[0][c])
    next = set()
    depth = 0

    above_odd = [(1,1), (1,0), (1, -1)]
    above_even = [(0,1), (1,0), (0, -1)] # for a hex in an even column


    while len(opens):
        # print('depth', depth)
        seen.update(opens)
        for row,col in opens:
            # print(row,col)
            hmap[row][col].depth = depth
            if col % 2 == 0:
                above = above_even
            else:
                above = above_odd
            # print(depth, above)
            for r,c in above:
                if hmap.valid_cell((row+r, col+c)) and hmap[row+r][col+c] and (row+r, col+c) not in seen:
                    next.add((row+r, col+c))
        depth += 1

        opens = next
        next = set()
    print('done')

def get_open(hmap):
    out = []
    for row in range(1, hmap.rows):
        for col in range(hmap.cols):
            if hmap[row][col] != 0 and not hmap[row][col].open:
                neighbors = hmap.named_neighbors((row, col))
                above = (neighbors['t'] and not neighbors['t'].open) or (neighbors['tl'] and not neighbors['tl'].open) or (neighbors['tr'] and not neighbors['tr'].open)
                below = (neighbors['b'] and not neighbors['b'].open) or (neighbors['bl'] and not neighbors['bl'].open) or (neighbors['br'] and not neighbors['br'].open)

                if above and below:
                    pass
                    # hmap[row][col].depth = 1
                else:
                    # hmap[row][col].depth = 0
                    out.append((row, col))
    return out

def clear_forces(hmap):
    for row in range(hmap.rows):
        for col in range(hmap.cols):
            if hmap[row][col] != 0:
                hmap[row][col] = Node()

def calculate_forces():
    calculate_depth(hmap)
    layers = defaultdict(set)

    for row in range(hmap.rows):
        for col in range(hmap.cols):
            if hmap[row][col] != 0:
                layers[hmap[row][col].depth].add((row, col))


    for depth in sorted(layers.keys(), reverse=True)[:-1]:
        print(layers[depth])
        # for row, col in layers[depth]:

def propogate_force(row, col):
    below_odd = [(-1, 0), (0,1), (0,-1)]
    below_even = [(-1, 0), (-1, 1), (-1,-1)] # for a hex in an even column

    node = hmap[row][col]
    force = node.force_left + node.force_center + node.force_right

    belows = []
    if col % 2 == 0:
        below = below_even
    else:
        below = below_odd

    neighbors = hmap.named_neighbors((row, col))

    total = 0.0
    total += neighbors['b'] and not neighbors['b'].open
    total += neighbors['br'] and not neighbors['br'].open
    total += neighbors['bl'] and not neighbors['bl'].open
    # print(depth, force, total)

    # if depth
    if total != 0:
        if neighbors['b'] and not neighbors['b'].open:
            neighbors['b'].force_center += force/total

        if neighbors['br'] and not neighbors['br'].open:
            neighbors['br'].force_left += force/total

        if neighbors['bl'] and not neighbors['bl'].open:
            neighbors['bl'].force_right += force/total
    else:
        # assert(False)
        total = 0.0
        total += neighbors['t'] and not neighbors['t'].open
        total += neighbors['tr'] and not neighbors['tr'].open
        total += neighbors['tl'] and not neighbors['tl'].open
        if total == 0:
            return
        # if total
        if neighbors['t'] and not neighbors['t'].open:
            neighbors['t'].force_center += force/total

        if neighbors['tr'] and not neighbors['tr'].open:
            neighbors['tr'].force_left += force/total

        if neighbors['tl'] and not neighbors['tl'].open:
            neighbors['tl'].force_right += force/total

def pixel_to_hex(x, y):
    y = h-y
    q = x * 2/3 / radius
    r = (-x / 3 + SQRT3/3 * y) / radius
    return (r,q)

hmap = Map((8,8), value=0)
for row, col in [(0, 4), (1, 2), (1, 4), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 1), (3, 4), (4, 1), (4, 4), (5, 2), (5, 3), (5, 4), (6, 1), (6, 2)]:
    hmap[row][col] = Node()
# hmap[0][4] = Node()
# hmap[1][4] = Node()
# hmap[2][4] = Node()
# hmap[2][3] = Node()
# hmap[2][5] = Node()
# hmap[3][4] = Node()
# hmap[4][4] = Node()

def draw():
    screen.fill((255,255,255))
    draw_hex_map(screen, hmap)
    pygame.display.flip()

def step():
    open_nodes = get_open(hmap)

    for row, col in open_nodes:
        hmap[row][col].open = True
        propogate_force(row, col)
    draw()


step()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # print(';space')
                step()
        if event.type == pygame.MOUSEBUTTONUP:
            clear_forces(hmap)

            row, col = pixel_to_hex(*pygame.mouse.get_pos())
            row = round(row)
            col = round(col)

            # print(row, col)

            if hmap[row][col] != 0:
                hmap[row][col] = 0
            else:
                hmap[row][col] = Node()

            derp = []
            for row in range(hmap.rows):
                for col in range(hmap.cols):
                    if hmap[row][col] != 0:
                        derp.append((row, col))
            print(derp)

            step()
