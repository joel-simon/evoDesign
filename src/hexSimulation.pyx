import math
import random
import time
import copy

from .cell import Cell
from .physics.empty_framework import Framework
from .physics.hexBody import HexBody
from .hexmap import Map
SQRT3 = math.sqrt( 3 )

class HexSimulation(object):
    def __init__(self, genome, bounds, verbose=False,
                max_steps=100, max_physics_step=10):
        self.hmap = Map(bounds, None)
        self.genome = genome

        self.physics = Framework()
        self.world = self.physics.world

        self.verbose = verbose
        self.max_steps = max_steps

        self.cells = []
        self.next_cell_id = 0
        self.last_change = 0

        self.hex_radius = 5
        self.bounds = bounds

        self.step_count = 0
        self.max_physics_step = max_physics_step

        # Step statistics
        self.created_cells = 0
        self.destroyed_cells = 0

    def _get_id(self):
        self.next_cell_id += 1
        return self.next_cell_id

    def _get_outputs(self):
        return [cell.outputs() for cell in self.hmap]

    def _coords_to_xy(self, coords):
        row, col = coords
        offset = self.hex_radius * SQRT3 / 2 if col % 2 else 0
        left = 1.5 * col * self.hex_radius
        top = offset + SQRT3 * row * self.hex_radius
        return [left, top]

    def create_cell(self, coords, cell_type=0):
        assert(self.hmap.valid_coords(coords))
        assert(not self.hmap[coords])
        self.last_change = self.step_count
        body = None

        xy = self._coords_to_xy(coords)
        xy[1] += self.hex_radius

        neighbors = list(self.hmap.neighbors(coords))
        static = []
        if coords[0] == 0:
            static = ['bottom_left', 'bottom_right']

        body = HexBody(self.world, xy, self.hex_radius, neighbors=neighbors, static=static)
        cell = Cell(self._get_id(), self.genome, body)

        cell.userData['coords'] = coords
        body.userData['cell'] = cell

        self.hmap[coords] = cell
        self.cells.append(cell)

        self.created_cells += 1
        return cell

    def destroy_cell(self, cell):
        self.last_change = self.step_count
        if cell.body:
            cell.body.destroy()
        self.cells.remove(cell)
        self.hmap[cell.userData['coords']] = 0
        self.destroyed_cells += 1

    def divide_cell(self, cell, direction):
        coords = self.hmap.neighbor(cell.userData['coords'], direction)
        if self.hmap.valid_coords(coords) and not self.hmap[coords]:
            self.last_change = self.step_count
            self.create_cell(coords)

    def create_inputs(self, cell):
        raise NotImplemented

    def handle_outputs(self, cell):
        raise NotImplemented

    def step(self, renderer=None):
        if self.verbose:
            print('#'*40,'step', self.step_count,'#'*40)

        self.created_cells = 0
        self.destroyed_cells = 0
        # kill_cells = []

        for cell in copy.copy(self.cells):
            inputs = self.create_inputs(cell)
            self.handle_outputs(cell, cell.network.serial_activate(inputs))

        for body in self.world.bodies:
            if body.userData and body.userData['origin']:
                body.position = body.userData['origin']
                body.linearVelocity = (0,0)
                body.angularVelocity = 0

        # self.physics.run(self.max_physics_step)

        if renderer:
            renderer.render(self)

        if self.verbose:
            print('destroyed %i cells' % self.destroyed_cells)
            print('created %i cells:' % self.created_cells)
            print('final cells: %i' % len(self.cells))


        assert(len(self.cells) <= self.bounds[0] * self.bounds[1])
        self.step_count += 1

    def run(self, renderer=None):
        for _ in range(self.max_steps):
            self.step(renderer)
            if self.step_count - self.last_change > 3:
                break
