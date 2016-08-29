# from src.springs.Spring2D import Body, StaticBody
from colorsys import hsv_to_rgb

from src.views.drawUtils import draw_line, draw_circle, draw_polygon, \
                                draw_text, xy_to_screen, rgb_int
import numpy as np
def drawFeaWorld(world, U, F, surface):
    scale = 1 # TODO: calculate scale here.
    derpa = np.array(world.coords) + U.T
    min_fos = 10
    for coord, re in zip(derpa, world.reactions):
        position = xy_to_screen(coord[0], coord[1], surface)
        if sum(re) == 3:
            draw_circle(surface, position, 3, (0, 0, 0))
        else:
            draw_circle(surface, position, 1, (20, 100, 20))

    for conn, force in zip(world.connections, F):
        c1 = derpa[conn[0]]
        c2 = derpa[conn[1]]
        p1 = xy_to_screen(c1[0], c1[1], surface)
        p2 = xy_to_screen(c2[0], c2[1], surface)
        if force == 0:
            color = hsv_to_rgb(0,0,0)
        else:
            min_fos = min(abs(344*pow(10, 6)/force), min_fos)
            color = rgb_int(hsv_to_rgb(9.0/255, 1, 1-344*pow(10, 6)/abs(force)))

        draw_line(surface, p1, p2, color, 1)
    # print F
    # print 1/F
    draw_text(surface, (0, 5), "n_joints:%i"%len(world.joints))
    draw_text(surface, (0, 30), "n_members:%i"%len(world.members))
    draw_text(surface, (0, 55), "FOS:%f"% min_fos)
