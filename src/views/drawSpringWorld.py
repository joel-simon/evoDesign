from src.springs.Spring2D import Body, StaticBody
from src.views.drawUtils import draw_line, draw_circle, draw_polygon, \
                                draw_text, xy_to_screen

def draw_joint(surface, joint, color = (10, 10, 10)):
    p1 = xy_to_screen(joint.bodyA.position[0], joint.bodyA.position[1], surface)
    p2 = xy_to_screen(joint.bodyB.position[0], joint.bodyB.position[1], surface)
    draw_line(surface, p1, p2, color, 1)

def draw_body(surface, body):
    x = body.position[0]
    y = body.position[1]
    position = xy_to_screen(x, y, surface)
    radius = 1

    if isinstance(body, StaticBody):
        draw_circle(surface, position, radius, (10, 10, 10))
    else:
        draw_circle(surface, position, radius, (20, 100, 20))

def drawSpringWorld(world, surface):
    scale = 1 # TODO: calculate scale here.
    max_force = 0.0

    for joint in world.joints:
        force = joint.GetReactionForce()
        max_force = max(force, max_force)
        color_diff = int(force * 512)
        color_diff = min(127, max(0, color_diff))
        color = (128+color_diff, 128-color_diff, 128-color_diff)
        draw_joint(surface, joint, color)

    for body in world.bodies:
        draw_body(surface, body)

    # scale(surface, (100, 100), DestSurface = None)

    draw_text(surface, (0, 5), "n_bodies:%i"%len(world.bodies))
    draw_text(surface, (0, 30), "n_joints:%i"%len(world.joints))
    draw_text(surface, (0, 55), "max_joint_force:%f"%max_force)
