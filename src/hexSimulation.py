import math
import random
import time
import copy

from .cell import Cell
# from .physics.empty_framework import Framework

# from .physics.hexBody import HexBody

from .springs.Spring2D import World


from .hexmap import Map
from .morphogens import reaction_diffusion

SQRT3 = math.sqrt( 3 )

class HexSimulation(object):
    def __init__(self, genome, bounds=(8,8), verbose=False,
                max_steps=100, max_physics_step=100, cellData = dict(),
                break_on_repeat=False):

        self.genome = genome
        self.hmap = Map(bounds, None)

        self.break_on_repeat = break_on_repeat
        if self.break_on_repeat:
            self.seen_states = set()

        # self.physics = Framework()
        # self.world = self.physics.world
        # self.world = World()

        self.cellData = cellData

        self.verbose = verbose
        self.max_steps = max_steps

        self.cells = []
        self.next_cell_id = 0
        self.last_change = 0

        self.hex_radius = 5
        self.bounds = bounds

        self.max_physics_step = max_physics_step

        # Step statistics
        self.step_count = 0
        self.created_cells = 0
        self.destroyed_cells = 0

    def _get_id(self):
        self.next_cell_id += 1
        return self.next_cell_id

    def _coords_to_xy(self, coords):
        row, col = coords
        offset = self.hex_radius * SQRT3 / 2 if col % 2 else 0
        left = 1.5 * col * self.hex_radius
        top = offset + SQRT3 * row * self.hex_radius
        return [left, top]

    def create_cell(self, coords, cell_type=0):
        assert(self.hmap.valid_coords(coords))
        assert(not self.hmap[coords])

        if self.hmap[coords]:
            return None

        self.last_change = self.step_count
        body = None

        # xy = self._coords_to_xy(coords)
        # xy[1] += self.hex_radius

        # neighbors = list(self.hmap.neighbors(coords))
        # static = []
        # if coords[0] == 0:
        #     static = ['bottom_left', 'bottom_right']

        # body = HexBody(self.world, xy, self.hex_radius, neighbors=neighbors, static=static)
        cell = Cell(self._get_id(), self.genome, body, copy.copy(self.cellData))

        cell.userData['coords'] = (coords[0], coords[1])
        # body.userData['cell'] = cell

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
        parent_coords = cell.userData['coords']
        coords = self.hmap.neighbor(parent_coords, direction)

        if self.hmap.valid_coords(coords) and not self.hmap[coords]:
            # self.hmap[parent_coords] = 0
            # cell.userData['coords'] = coords
            # self.hmap[coords] = cell
            # self.create_cell(parent_coords)
            self.create_cell(coords)

    def create_inputs(self, cell):
        raise NotImplemented

    def handle_outputs(self, cell):
        raise NotImplemented

    def clear_state(self):
        pass

    def step(self, renderer=None):
        if self.verbose:
            print('#'*40,'step', self.step_count,'#'*40)

        self.created_cells = 0
        self.destroyed_cells = 0

        # First collect all inputs before active on them so simulation
        # state does not change during input collection
        all_outputs = []
        for cell in self.cells:
            inputs = self.create_inputs(cell)

            for module in self.genome.gene_modules:
                inputs.extend(module.create_input(cell, self))
            assert(len(inputs) == self.genome.num_inputs)
            all_outputs.append(cell.outputs(inputs))
            assert(len(all_outputs[-1]) == self.genome.num_outputs)

        # Make a list copy because self.cells will change during iteration.
        for cell, out in list(zip(self.cells, all_outputs)):
            nmi = self.genome.non_module_outputs
            self.handle_outputs(cell, out[:nmi])
            self.genome.gene_modules[0].handle_output(cell, out[nmi:])

        ### PHYSICS
        # Reset Bodies
        # for body in self.world.bodies:
        #     if body.userData and body.userData['origin']:
        #         body.position = body.userData['origin']
        #         body.linearVelocity = (0,0)
        #         body.angularVelocity = 0

        # for i in range(self.max_physics_step):
        #     self.physics.Step(self.physics.settings)
        #     if renderer:
        #         renderer.render(self)
        #####

        if self.verbose:
            print('destroyed %i cells' % self.destroyed_cells)
            print('created %i cells:' % self.created_cells)
            print('final cells: %i' % len(self.cells))

        assert(len(self.cells) <= self.bounds[0] * self.bounds[1])
        self.step_count += 1

    def run(self, renderer=None):
        if renderer:
            renderer.render(self)

        for _ in range(self.max_steps):
            self.step(renderer)
            if renderer:
                renderer.render(self)
            # if self.step_count > 3:
            #     fitness = self.fitness()
            #     min_fitness = self.step_count / float(self.max_steps)
            #     if fitness < min_fitness:
            #         return fitness
            if self.step_count - self.last_change > 5:
                break

            if self.break_on_repeat:
                state_hash = self.hmap.hash()
                if state_hash in self.seen_states:
                    return self.fitness()
                self.seen_states.add(state_hash)

        return 0.0


