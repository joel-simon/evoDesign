import os
import math
import numpy as np

from src.simulation import Simulation
from src.modules import neighbors_distinct, divide_distinct, truss

from src.map_utils import shape, connected_mask
from src.balance import balance_score

BOUNDS = (7, 7, 7)
STEPS = int(BOUNDS[0] * BOUNDS[1] * BOUNDS[1] / 2.0)

static_map = np.zeros(BOUNDS)
static_map[0] = 0b110000 # X axis=0 (the wall) is static

genome_config = {
    'modules': [
        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {}),
        (truss.TrussModule, {'static_map': static_map}),
    ],
    'inputs': ['gradient'],
    'outputs': [('apoptosis', 'sigmoid')]
}

class Simulation(Simulation):
    """docstring for Simulation"""
    def __init__(self, genome):
        super(Simulation, self).__init__(genome, max_steps=STEPS, bounds=BOUNDS)
        # Create starting cells.
        self.create_cell(0,0,0)

        self.legroom = []
        self.legroom_fitness = 0
        self.total_fitness = 0
        self.fos_fitness = 0

    def step(self):
        pass
        # self._mark_unconnected()
        # for cell in self.cells:
        #     if cell.userData['connected'] and 'body' not in cell.userData:
        #         self.module_simulations[2]._create_body(cell)
        #     elif not cell.userData['connected'] and 'body' in cell.userData:
        #         cell.userData['body'].destroy()
        #         del cell.userData['body']

    def cell_init(self, cell):
        cell.userData['connected'] = True

    def create_input(self, cell):
        gradient = cell.position[1] / float(self.bounds[1])
        # gradient = cell.position[1] / float(self.bounds[1])
        return [gradient]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def _apply_loads(self, truss):
        for x in range(self.bounds[0]):
            for z in range(self.bounds[2]):
                cell = self.hmap[x][-1][z]
                if cell and 'body' in cell.userData:
                    body = cell.userData['body']
                    body.joints[4].loads[1] = -1e4
                    body.joints[5].loads[1] = -1e4
                    body.joints[6].loads[1] = -1e4
                    body.joints[7].loads[1] = -1e4

    def _legroom_fitness(self):
        """ Calculate the amount of legroom under the table.
            Defined as the largest
        """
        heights = [0] * self.bounds[1]
        for cell in self.cells:
            if cell.userData['connected']:
                rc = cell.position
                heights[rc[1]] = max(heights[rc[1]], rc[0])

        visited = set()
        queue = [(0, c) for c in range(self.bounds[1]) if not self.hmap[0][c]]

        while queue:
            coord = queue.pop()
            if coord not in visited:
                visited.add(coord)
                next = self.hmap.neighbor_coords(coord, filter_valid=True)
                queue.extend([c for c in next if self.hmap[c] == False])

        legroom = [rc for rc in visited if heights[rc[1]] > rc[0] ]
        self.legroom = legroom
        # open_cols = sum(1 for h in heights if h > 0)
        return len(legroom) / float((self.bounds[0]-1) * (self.bounds[1]-1))

    # def _connected(self, rc):
    #     return self.hmap[rc] and self.hmap[rc].userData['connected']

    def fitness(self):
        if len(self.cells) == 0:
            return 0

        X, Y, Z = shape(self.hmap)

        connected_array = connected_mask(self.hmap)
        connected_cells = [ ]
        for c in self.cells:
            if connected_array[c.position]:
                c.userData['connected'] = True
                connected_cells.append(c)
            else:
                c.userData['connected'] = False
        y_max = 0
        top_covereage = 0
        for cell in connected_cells:
            y_max = max(y_max, cell.position[1])
            top_covereage += (cell.position[1] == Y-1)

        height_fitness = y_max / float(Y)
        cover_fitness = top_covereage / float(X * Z)

        truss = self.module_simulations[2].truss
        self._apply_loads(truss)
        truss.calc_fos()
        fos = truss.fos_total
        fos_fitness = (math.atan((fos - 1) * 10) / math.pi) + 0.5

        # num_bodies = sum(1 for c in self.cells if 'body' in c.userData)
        weight_fitness = 1 - (len(connected_cells) / float(X*Y*Z))

        legroom_fitness = 1#self._legroom_fitness()
        # legroom_fitness = self._legroom() / float((self.bounds[0]-1) * (self.bounds[1]-1))

        balance_fitness = balance_score(connected_cells, connected_array, self.verbose)

        total_fitness = cover_fitness * weight_fitness * balance_fitness * fos_fitness

        if self.verbose:
            print 'balance_fitness', balance_fitness
            print 'fos', fos
            print 'fos_fitness', fos_fitness
        # self.total_fitness = total_fitness
        # self.legroom_fitness = legroom_fitness
            # self.fos_fitness = fos_fitness

        return total_fitness

    def render(self, surface):
        pass
