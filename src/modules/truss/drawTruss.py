# from src.springs.Spring2D import Body, StaticBody
from colorsys import hsv_to_rgb

from src.views.drawUtils import draw_line, draw_circle, draw_polygon, \
                                draw_text, xy_to_screen, rgb_int
import numpy
# import numpy as np
def joint_to_screen(joint, surface):
    position = joint.coordinates# + joint.deflections.T[0]
    return xy_to_screen(position[0], position[1], surface)

def drawTruss(truss, surface):
    scale = 1 # TODO: calculate scale here.
    
    for joint in truss.joints:
        p = joint_to_screen(joint, surface)
        if joint.translation.sum() == 3:
            draw_circle(surface, p, 3, (0, 0, 0))
        else:
            draw_circle(surface, p, 1, (20, 100, 20))

    min_force = min(abs(m.force) for m in truss.members)
    max_force = max(abs(m.force) for m in truss.members)

    for member in truss.members:
        p0 = joint_to_screen(member.joints[0], surface)
        p1 = joint_to_screen(member.joints[1], surface)
        v = (member.force - min_force) / (max_force - min_force)
        if max_force == min_force:
            color = (0,0,0)
        else:
            color = rgb_int(hsv_to_rgb(9.0/360, 1, v))

        draw_line(surface, p0, p1, color, 1)
    # print F
    # print 1/F
    draw_text(surface, (5, 5), "n_joints:%i"%len(truss.joints))
    draw_text(surface, (5, 30), "n_members:%i"%len(truss.members))
    draw_text(surface, (5, 55), "FOS:%f"% truss.fos_total)
