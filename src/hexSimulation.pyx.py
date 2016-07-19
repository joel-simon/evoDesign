import math
import random
import time

from src.cell import Cell
from .physics.empty_framework import Framework
from .physics.hexBody import HexBody
# from .hexmap import Map
cdef long SQRT3 = math.sqrt( 3 )


cdef int simulate(genome, int rows, int cols, int max_steps):
    cdef int next_cell_id, last_change_step, hex_radius, step_count

    cdef int[rows][cols]

    cells = []

    physics = Framework()
    world = self.physics.world
     = 0


class Simulation(object):
    def __init__(self, genome, bounds, verbose=False,
                max_steps=100, max_physics_step=10, Renderer=None):
        if Renderer:
            self.renderer = Renderer(self)
        else:
            self.renderer = None

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
        self.last_change = self.step_count

        body = None
        xy = self._coords_to_xy(coords)
        xy[1] += self.hex_radius

        neighbors = self.hmap.neighbors(coords, labels=True)
        for k, v in neighbors.items():
            if v and v.body:
                neighbors[k] = v.body

        static = []
        if coords[0] == 0:
            static = ['bottom_left', 'bottom_right']

        body = HexBody(self.world, xy, self.hex_radius, neighbors=neighbors, static=static)
        cell = Cell(self._get_id(), self.genome, body)

        cell.userData['coords'] = coords
        body.userData['cell'] = cell

        self.hmap[coords] = cell
        self.cells.append(cell)

        return cell

    def destroy_cell(self, cell):
        self.last_change = self.step_count
        # cell.body.destroy()
        self.cells.remove(cell)
        self.hmap[cell.userData['coords']] = 0

    def divide_cell(self, cell, direction):
        coords = self.hmap.neighbor(cell.userData['coords'], direction)
        if self.hmap.valid_coords(coords) and not self.hmap[coords]:
            self.last_change = self.step_count
            self.create_cell(coords)

    def step(self):
        if self.verbose:
            print('step', self.step_count)
            print('\t', len(self.cells))
        kill_cells = []

        for cell in self.cells:
            cell.step(self)

        for body in self.world.bodies:
            if body.userData and body.userData['origin']:
                body.position = body.userData['origin']
                body.linearVelocity = (0,0)
                body.angularVelocity = 0


        # self.physics.run(self.max_physics_step)

        if self.renderer:
            self.renderer.render()

        assert(len(self.cells) <= self.bounds[0] * self.bounds[1])
        self.step_count += 1

    def run(self):
        for _ in range(self.max_steps):
            self.step()
            if self.step_count - self.last_change > 3:
                break
