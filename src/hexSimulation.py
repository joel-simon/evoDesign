import math
import random
import time

from src.cell import Cell
from Box2D import *
from .physics.framework import Framework
from .physics.hexBody import HexBody
from .hexmap import Map
SQRT3 = math.sqrt( 3 )
def joint_between(bodyA, bodyB):
    for jointEdge in bodyA.joints:
        if jointEdge.other == bodyB:
            return jointEdge.joint
    return None

class Simulation(Framework):
    def __init__(self, genome, bounds=200, verbose=False, max_steps=100):
        super(Simulation, self).__init__()

        # self.renderer = MyDraw(surface=self.screen, test=self)
        # self.world.renderer = None#self.renderer
        self.hmap = Map((bounds, bounds), None)
        self.genome = genome
        self.verbose = verbose
        self.max_steps = max_steps

        self.cells = []
        self.next_cell_id = 0
        self.steps_since_change = 0

        self.joints = []
        self.contacts = []

        self.break_thresshold = 1000

        self.world.DestroyBody(self.world.bodies[0])
        self.pause = False

        self.hex_radius = 10
        self.bounds = bounds


        # if bounds != None:
        #     t = 20
        #     w = bounds
        #     # Floor
        #     self._create_static_box(position=(0,-t/2),dimensions=(w/2,t/2))
            # Ceiling
            # self._create_static_box(position=(0,w+t/2),dimensions=(w/2,t/2))
            # Walls
            # self._create_static_box(position=((-w-t)/2,w/2),dimensions=(t/2,w/2+t))
            # self._create_static_box(position=((w+t)/2,w/2),dimensions=(t/2,w/2+t))

    def _create_static_box(self, position, dimensions):
      self.world.CreateStaticBody(
        position=position,
        shapes=b2PolygonShape(box=dimensions),
        userData={'type': 'bounds', 'parents': set([])}
      )

    def _get_id(self):
        self.next_cell_id += 1
        return self.next_cell_id

    def _get_outputs(self):
        return [cell.outputs() for cell in self.cells]

    def _coords_to_xy(self, coords):
        row, col = coords
        offset = self.hex_radius * SQRT3 / 2 if col % 2 else 0
        left = 1.5 * col * self.hex_radius
        top = offset + SQRT3 * row * self.hex_radius
        return [left, top]

    def create_cell(self, coords, cell_type=0):
        assert(self.hmap.valid_coords(coords))
        xy = self._coords_to_xy(coords)
        xy[1] += self.hex_radius

        neighbors = self.hmap.neighbors(coords, labels=True)
        static = []
        if coords[0] == 0:
            static = ['bottom_left', 'bottom_right']

        body = HexBody(self.world, xy, self.hex_radius, neighbors=neighbors, static=static)
        cell = Cell(self._get_id(), self.genome, body)

        body.userData['cell'] = cell
        self.hmap[coords] = body
        return cell

    # Extend framework
    def BeginContact(self, contact):
        self.contacts.append(contact)

    def handle_outputs(self, outputs):
        new_cells = []
        for cell, output in zip(self.cells, outputs):
            if 'apoptosis' in output and output['apoptosis']:
                self.kill_cells.append(cell)
                continue #Cannot apoptosis and do other things.

            # CELL GROWTH
            if 'divide' in output:
                daughter_body = cell.body.divide(angle=math.pi/2)
                new_cells.append(self.create_cell(None, None, body=daughter_body))

        return new_cells
            # if 'contract' in output:
            #     cell.body.contract

    def Step(self, settings):
        if self.pause:
            settings.pause = True
            super(Simulation, self).Step(settings)
            return

        print('step', self.stepCount)
        kill_cells = []
        # nuke_bodies = set()
        # Compute internal logic for cell bodies
        outputs = self._get_outputs()
        new_cells = self.handle_outputs(outputs)

        forces = []
        for joint in self.world.joints:
            forces.append(joint.GetReactionForce(.60).Normalize())
        print(max(forces))

        # for cell in kill_cells:
        #     self.cell.body.destroy()
        #     self.cells.remove(cell)

        # for body in nuke_bodies:
        #     self.world.DestroyBody(body)

        self.contacts = []
        self.cells.extend(new_cells)
        super(Simulation, self).Step(settings)
