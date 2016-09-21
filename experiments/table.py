import os
import math
import numpy

# from main import main
from src.hexSimulation import HexSimulation
from src.hexmap import Map
from src.modules import signals, neighbors_distinct, divide_distinct, truss
from src.views.drawHexMap import draw_hex_map
from src.views.drawUtils import draw_text

SIMULATION_BOUNDS = (13, 19)
SIMULATION_STEPS = int(SIMULATION_BOUNDS[0] * SIMULATION_BOUNDS[1] / 2.0)

static_map = Map(SIMULATION_BOUNDS)
for col in range(0, SIMULATION_BOUNDS[1]):
    static_map[0][col] = 0b110000


genome_config = {
    'modules': [
        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {}),
        (truss.TrussModule, {'static_map': static_map}),
    ],
    'inputs': ['gradient'],
    'outputs': [('apoptosis', 'sigmoid')]
}

class Simulation(HexSimulation):
    """docstring for Simulation"""
    def __init__(self, genome):
        super(Simulation, self).__init__(genome, max_steps=SIMULATION_STEPS,
                                         bounds=SIMULATION_BOUNDS, break_on_repeat=False)

        # CREATE STARTING CELLS: one in top-left corner.
        # self.starts = [(0, int(self.bounds[1]/2))]
        self.starts  = [(0,0)]
        self.create_cell(self.starts[0])

        self.legroom = []
        self.legroom_fitness = 0
        self.total_fitness = 0
        self.fos_fitness = 0

    def step(self):
        self._mark_unconnected()
        for cell in self.cells:
            if cell.userData['connected'] and 'body' not in cell.userData:
                self.module_simulations[2]._create_body(cell)
            elif not cell.userData['connected'] and 'body' in cell.userData:
                cell.userData['body'].destroy()
                del cell.userData['body']

    def coords_xy(self, coords):
        row, col = coords
        offset = math.sqrt(3) / 2 if col % 2 else 0
        left = 1.5 * col
        top = offset + math.sqrt(3) * row
        return (left, top)

    def cell_init(self, cell):
        cell.userData['connected'] = True
        cell.userData['xy'] = self.coords_xy(cell.userData['coords'])

    def create_input(self, cell):
        gradient = cell.userData['coords'][1] / float(self.bounds[1])
        return [gradient]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def _apply_loads(self, truss):
        for col in range(self.hmap.shape[1]):
            if self.hmap[-1][col] and 'body' in self.hmap[-1][col].userData:
                body = self.hmap[-1][col].userData['body']
                body.joints['top_right'].loads[1] = -1e3
                body.joints['top_left'].loads[1] = -1e3

    def _mark_unconnected(self):
        seen = set()
        queue = []

        for col in range(self.bounds[1]):
            if self.hmap[0][col]:
                queue.append((0, col))

        while queue:
            node = queue.pop()
            if node not in seen:
                seen.add(node)
                for rc in self.hmap.neighbor_coords(node, filter_valid=True):
                    if self.hmap[rc]:
                        queue.append(rc)

        for cell in self.cells:
            if cell.userData['coords'] in seen:
                cell.userData['connected'] = True
            else:
                cell.userData['connected'] = False

    def _legroom_fitness(self):
        """ Calculate the amount of legroom under the table.
            Defined as the largest
        """
        heights = [0] * self.bounds[1]
        for cell in self.cells:
            if cell.userData['connected']:
                rc = cell.userData['coords']
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

    def _balance_fitness(self):
        if len(self.cells) == 0:
            return 0

        # x, y = 0, 0
        X = 0
        floor_left = None
        floor_right = None

        for cell in self.cells:
            x = cell.userData['xy'][0]
            X += x
            # y += cell.userData['xy'][1]
            # On floor
            if cell.userData['coords'][0] == 0:
                if x < floor_left or floor_left is None:
                    floor_left = x
                if x > floor_right or floor_right is None:
                    floor_right = x

        # Nothing on floor.
        if floor_left is None or floor_right is None:
            return 0

        X /= float(len(self.cells))

        center = (floor_left + floor_right) / 2

        d = abs(X - center) / (floor_right - center + .1)

        width = self.coords_xy((0, self.bounds[1]))[0]

        return math.exp(-2*d**2) * (floor_right-floor_left) / width

    # def _balance_fitness(self):
    #     truss = self.module_simulations[2].truss
    #     truss.calc_center_of_mass()
    #     com = truss.center_of_mass

    #     if len(truss.members) == 0:
    #         return 0

    #     X = [j.coordinates[0] for j in truss.joints if j.translation.sum() == 3]

    #     if len(X) == 0:
    #         return 0

    #     left = min(X)
    #     right = max(X)
    #     center = (left + right) / 2

    #     x = abs(com[0] - center) / (right - center)

    #     return math.exp(-2*x**2) #(right-left) *

    def _connected(self, rc):
        return self.hmap[rc] and self.hmap[rc].userData['connected']

    def fitness(self):
        N = float(self.bounds[0]*self.bounds[1])

        if len(self.cells) == 0:
            return 0

        max_row = max([rc[0] for rc in self.hmap.coords() if self._connected(rc)] or [0])
        height_fitness = (max_row / float(self.bounds[0] - 1))

        on_top = sum(1 for c in range(self.bounds[1]) if self._connected((-1, c)))
        cover_fitness = on_top / float(self.hmap.shape[1])

        # if cover_fitness + height_fitness < .9:
        #     return (cover_fitness + height_fitness)/2

        truss = self.module_simulations[2].truss
        self._apply_loads(truss)
        truss.calc_fos()
        fos = truss.fos_total
        fos_fitness = (math.atan((fos - 1) * 10) / math.pi) + 0.5
        # fos_fitness = 1 / (1 + math.exp(-10*(fos-1)))

        # num_bodies = sum(1 for c in self.cells if 'body' in c.userData)
        weight_fitness = 1 - (len(self.cells) / N)

        legroom_fitness = self._legroom_fitness()
        # legroom_fitness = self._legroom() / float((self.bounds[0]-1) * (self.bounds[1]-1))


        total_fitness = height_fitness * cover_fitness * legroom_fitness * \
                        self._balance_fitness() * fos_fitness

        # save data for rendering
        self.total_fitness = total_fitness
        self.legroom_fitness = legroom_fitness
        self.fos_fitness = fos_fitness

        return total_fitness

    def _draw_hex(self, coord, hexview):
        if self.hmap[coord]:
            if self._connected(coord):
                hexview.fill((160, 160, 160))
            else:
                hexview.fill((220, 220, 220))
        if coord in self.legroom:
            hexview.fill((0, 0, 200))
        hexview.border()

    def render(self, surface):
        draw_hex_map(surface, self.hmap, self._draw_hex)
        draw_text(surface, (2, 10), "Num cells:%i"%len(self.cells))
        draw_text(surface, (2, 50), "legroom fitness:%f"%self.legroom_fitness)
        draw_text(surface, (2, 70), "FOS fitness :%f"%self.fos_fitness)
        draw_text(surface, (2, 90), "balance :%f"%self._balance_fitness())
        draw_text(surface, (2, 110), "total fitness :%f"%self.total_fitness)
