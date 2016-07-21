# from src.cell import Cell
# import random
# import time
# import math
# from Box2D import *
# from .physics.framework import Framework
# from .physics.softBody2 import SoftBody
# from copy import copy
# import traceback
# from .physics.backends.pygame_framework import PygameDraw

# def joint_between(bodyA, bodyB):
#     for jointEdge in bodyA.joints:
#         if jointEdge.other == bodyB:
#             return jointEdge.joint
#     return None

# class MyDraw(PygameDraw):
#     # pass
#     def __init__(self, **kwargs):
#         super(MyDraw, self).__init__(**kwargs)

#     def StartDraw(self, **kwargs):
#         super(MyDraw, self).StartDraw(**kwargs)

#     # def EndDraw(self, **kwargs):
#     #     super(MyDraw, self).EndDraw(**kwargs)


#     def DrawSolidPolygon(self, vertices, color):
#         # print('COLOR', color)
#         super(MyDraw, self).DrawSolidPolygon(vertices, color)

#     # def DrawSolidCircle(self, center, radius, axis, color):
#     #     print('COLOR', color)
#     #     super(MyDraw, self).DrawSolidCircle(center, radius, axis, color)

# class Simulation(Framework):
#     def __init__(self, genome, bounds=200, verbose=False, max_steps=100):
#         super(Simulation, self).__init__()

#         # self.renderer = MyDraw(surface=self.screen, test=self)
#         # self.world.renderer = None#self.renderer

#         self.genome = genome
#         self.verbose = verbose
#         self.max_steps = max_steps

#         self.cells = []
#         self.next_cell_id = 0
#         self.steps_since_change = 0

#         self.joints = []
#         self.contacts = []

#         self.nodes_per_body = 50
#         self.break_thresshold = 1000

#         self.world.DestroyBody(self.world.bodies[0])
#         self.pause = False

#         if bounds != None:
#             t = 20
#             w = bounds
#             # Floor
#             self._create_static_box(position=(0,-t/2),dimensions=(w/2,t/2))
#             # Ceiling
#             self._create_static_box(position=(0,w+t/2),dimensions=(w/2,t/2))
#             # Walls
#             self._create_static_box(position=((-w-t)/2,w/2),dimensions=(t/2,w/2+t))
#             self._create_static_box(position=((w+t)/2,w/2),dimensions=(t/2,w/2+t))

#     def _create_static_box(self, position, dimensions):
#       self.world.CreateStaticBody(
#         position=position,
#         shapes=b2PolygonShape(box=dimensions),
#         userData={'type': 'bounds', 'parents': set([])}
#       )

#     def _get_id(self):
#         self.next_cell_id += 1
#         return self.next_cell_id

#     def _get_outputs(self):
#         return [cell.outputs() for cell in self.cells]

#     def create_cell(self, position, bodies, cell_type=0, body=None):
#         if body == None:
#             body = SoftBody(self.world, position, bodies, verbose=self.verbose)
#         cell = Cell(self._get_id(), self.genome, body)
#         # self.cells.append(cell)
#         body.userData['cell'] = cell
#         return cell

#     # Extend framework
#     def BeginContact(self, contact):
#         self.contacts.append(contact)

#     def move_joint(self, joint, bodyA, bodyB):
#         new_joint = self.world.CreateDistanceJoint(
#             frequencyHz=joint.frequency,
#             dampingRatio=joint.dampingRatio,
#             bodyA=bodyA,
#             bodyB=bodyB,
#             localAnchorA=(0,0),
#             localAnchorB=(0,0),
#             collideConnected=joint.collideConnected,
#             userData = copy(joint.userData)
#         )

#         # if joint.other

#         self.world.DestroyJoint(joint)
#         return new_joint

#     def handle_outputs(self, outputs):
#         new_cells = []
#         for cell, output in zip(self.cells, outputs):
#             if 'apoptosis' in output and output['apoptosis']:
#                 self.kill_cells.append(cell)
#                 continue #Cannot apoptosis and do other things.

#             # CELL GROWTH
#             if 'grow' in output:
#                 cell.body.grow(output['grow'])
#                 if cell.body.area >= 2*cell.body.rest_area:
#                     daughter_body = cell.body.divide(angle=math.pi/2)
#                     new_cells.append(self.create_cell(None, None, body=daughter_body))

#             if 'divide' in output:
#                 daughter_body = cell.body.divide(angle=math.pi/2)
#                 new_cells.append(self.create_cell(None, None, body=daughter_body))

#             if 'contract' in output:
#                 cell.body.contract(math.pi/2, output['contract'])

#         return new_cells
#             # if 'contract' in output:
#             #     cell.body.contract

#     def Step(self, settings):
#         if self.pause:
#             settings.pause = True
#             super(Simulation, self).Step(settings)
#             return

#         print('step', self.stepCount)
#         kill_cells = []


#         nuke_bodies = set()
#         # Compute internal logic for cell bodies
#         try:
#             for cell in self.cells:
#                 cell.body.step()
#             outputs = self._get_outputs()
#             new_cells = self.handle_outputs(outputs)


#         except AssertionError as e:
#             traceback.print_exc()
#             self.pause = True
#             return

#         for cell in kill_cells:
#             self.cell.body.destroy()
#             self.cells.remove(cell)

#         for contact in self.contacts:
#             bodyA, bodyB = (contact.fixtureA.body, contact.fixtureB.body)

#             if bodyA in nuke_bodies or bodyB in nuke_bodies:
#                 continue

#             # if bodyA.userData == 'bounds' or bodyB.userData == 'bounds':
#             #     continue
#             # if bodyA.userData == None:
#             #     continue
#             # if bodyB.userData == None:
#             #     continue
#             if len(bodyA.userData['parents'].intersection(bodyB.userData['parents'])) > 0:
#                 continue

#             othersA = set(j.other for j in bodyA.joints)
#             othersB = set(j.other for j in bodyB.joints)

#             others = othersA.intersection(othersB)

#             if len(others) == 0:
#                 continue

#             # MERGE BODYB INTO BODYA
#             if self.verbose:
#                 print('MERGING JOINTS')
#                 print('len other', len(others))
#                 print('\tbodyA %i' %(bodyA.userData['id']))
#                 print('\tbodyB %i' %(bodyB.userData['id']))

#             for jointEdge in bodyB.joints:
#                 if jointEdge.other in others:
#                     joint_between(bodyA, jointEdge.other).userData['type'] = 'inner_wall'
#                     self.world.DestroyJoint(jointEdge.joint)
#                 else:
#                     self.move_joint(jointEdge.joint, jointEdge.other, bodyA)

#             for parentB in bodyB.userData['parents']:
#                 idx = parentB.bodies.index(bodyB)
#                 parentB.bodies.insert(idx, bodyA)
#                 parentB.bodies.remove(bodyB)
#                 bodyA.userData['parents'].add(parentB)

#             nuke_bodies.add(bodyB)
#             if self.verbose:
#                 for parentA in bodyA.userData['parents']:
#                     parentA.valid()
#                 for parentB in bodyB.userData['parents']:
#                     parentB.valid()

#         for body in nuke_bodies:
#             self.world.DestroyBody(body)

#         self.contacts = []
#         self.cells.extend(new_cells)

#         if isinstance(self.renderer, MyDraw):
#             colorA = b2Color(.1, .8, .1)
#             colorB = b2Color(.1, .1, .9)
#             for cell in self.cells:
#                 points = [self.renderer.to_screen(b.position) for b in cell.body.bodies]
#                 # if cell.body.internal_body:
#                 #     self.renderer.DrawSolidPolygon(points, colorB)
#                 # else:
#                 self.renderer.DrawSolidPolygon(points, colorA)

#         super(Simulation, self).Step(settings)
