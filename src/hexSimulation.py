import math
import random
import time
import copy

from .cell import Cell

# from .physics.empty_framework import Framework
# from .physics.hexBody import HexBody

from .hexmap import Map
from .morphogens import reaction_diffusion

SQRT3 = math.sqrt( 3 )

class HexSimulation(object):
    def __init__(self, genome, bounds, verbose=False,
                max_steps=100, max_physics_step=10):

        self.genome = genome
        self.hmap = Map(bounds, None)

        # Morphogen grids
        self.A  = [ Map(bounds, 0) for _ in range(genome.num_morphogens) ]
        self.I  = [ Map(bounds, 0) for _ in range(genome.num_morphogens) ]
        self.PA = [ Map(bounds, 0) for _ in range(genome.num_morphogens) ]
        self.PI = [ Map(bounds, 0) for _ in range(genome.num_morphogens) ]

        # self.physics = Framework()
        # self.world = self.physics.world

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

    def _step_morphogens(self):
        for i in range(self.genome.num_morphogens):
            morph_gene = list(self.genome.morphogen_genes.values())[i]
            values = morph_gene.values()
            reaction_diffusion.run(
                A=self.A[i].values,
                I=self.I[i].values,
                mask=self.hmap,
                PA=self.PA[i].values,
                PI=self.PI[i].values,
                Da=values['activator_diffusion'],
                Di=values['inhibitor_diffusion'],
                Ra=values['activator_removal'],
                Ri=values['inhibitor_removal'],
                saturate=values['saturate'],
                steps=200
            )

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

        # xy = self._coords_to_xy(coords)
        # xy[1] += self.hex_radius

        # neighbors = list(self.hmap.neighbors(coords))
        # static = []
        # if coords[0] == 0:
        #     static = ['bottom_left', 'bottom_right']

        # body = HexBody(self.world, xy, self.hex_radius, neighbors=neighbors, static=static)
        cell = Cell(self._get_id(), self.genome, body)

        cell.userData['coords'] = coords
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

        # Reinitialize morphogen production values.
        for row in range(self.bounds[0]):
            for col in range(self.bounds[1]):
                for i in range(self.genome.num_morphogens):
                    self.PA[i][row][col] = 0.0
                    self.PI[i][row][col] = 0.0

        for cell in copy.copy(self.cells):
            inputs = self.create_inputs(cell)
            # inputs.extend(self._morphogen_inputs(cell))

            # Compute outputs with NN
            outputs = cell.network.serial_activate(inputs)

            # Handle non morphogen outputs.
            self.handle_outputs(cell, outputs)


        #### MORPHOGENS
        self._step_morphogens()

        #### PHYSICS
        # Reset Bodies
        # for body in self.world.bodies:
        #     if body.userData and body.userData['origin']:
        #         body.position = body.userData['origin']
        #         body.linearVelocity = (0,0)
        #         body.angularVelocity = 0

        # self.physics.run(self.max_physics_step)
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

            if self.step_count > 3:
                fitness = self.fitness()
                min_fitness = self.step_count / float(self.max_steps)
                if fitness < min_fitness:
                    return fitness
            # if self.step_count - self.last_change > 3:
            #     break
        return fitness


