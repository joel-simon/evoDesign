# from src.springs.Spring2D import Body, StaticBody
from colorsys import hsv_to_rgb

from src.views.drawUtils import draw_line, draw_circle, draw_polygon, \
                                draw_text, xy_to_screen, rgb_int

def joint_to_screen(joint, surface):
    position = joint.coordinates + joint.deflections.T[0]
    return xy_to_screen(10*position[0], 10*position[1], surface)

def drawTruss(truss, surface):
    scale = 1 # TODO: calculate scale here.

    if len(truss.members):

        for i in range(len(truss.joints)):
            joint = truss.joints[i]
            coordinates = truss.coordinates[i]
            joint.coordinates = coordinates
            p = joint_to_screen(joint, surface)

            if truss.is_static(joint):
                draw_circle(surface, p, 5, (0, 0, 0))
            else:
                # TODO: draw load direction arrow
                if joint.loads.sum() != 0:
                    draw_circle(surface, p, 5, (200, 20, 20))
                else:
                    draw_circle(surface, p, 1, (20, 100, 20))

        min_fos = min(abs(m.fos) for m in truss.members)
        max_fos = max(abs(m.fos) for m in truss.members)

        for member in truss.members:
            p0 = joint_to_screen(member.joint_a, surface)
            p1 = joint_to_screen(member.joint_b, surface)

            if max_fos == min_fos:
                color = (0,0,0)
            else:
                v = (member.fos - min_fos) / (max_fos - min_fos)
                color = rgb_int(hsv_to_rgb(9.0/360, 1, v))

            draw_line(surface, p0, p1, color, 1)

        # com = truss.center_of_mass
        # p = xy_to_screen(com[0] * 10, com[1] * 10, surface)
        # draw_circle(surface, p, 5, (20, 20, 200))

    draw_text(surface, (5, 5), "n_joints:%i"%len(truss.joints))
    draw_text(surface, (5, 30), "n_members:%i"%len(truss.members))
    draw_text(surface, (5, 55), "FOS:%f"% truss.fos_total)
