import math

from src.hexSimulation import HexSimulation
from src.hexmap import Map

from src.modules import signals, light, water, truss, \
                        neighbors_distinct, divide_theta, divide_distinct

from src.views.drawHexMap import draw_hex_map
from src.views.drawUtils import draw_text

BOUNDS = (12, 9)
PERCENT_DIRT = .25
DIRT_HEIGHT = int(BOUNDS[0] * PERCENT_DIRT)
print DIRT_HEIGHT
dirt_map = Map(BOUNDS)
for row in range(0, DIRT_HEIGHT):
    for col in range(0, BOUNDS[1]):
        dirt_map[row][col] = 0b111111

def add_loads(hmap, truss):
    pass

genome_config = {
    'modules': [

        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {}),
        # (divide_theta.DivideThetaModule, {}),

        (light.LightModule, {'light_coverage': 1}),
        (water.WaterModule, {'production_map': dirt_map, 'cell_input': True}),
        (truss.TrussModule, {'static_map': dirt_map, 'add_loads': add_loads}),

    ],
    'inputs': ['underground'],
    'outputs': [('apoptosis', 'sigmoid')]
}

class Simulation(HexSimulation):
    """docstring for Simulation"""
    def __init__(self, genome):
        max_steps = int(BOUNDS[0] * BOUNDS[1] / 2.0)
        super(Simulation, self).__init__(genome, max_steps=max_steps,
                                         bounds=BOUNDS, break_on_repeat=True)
        self.start = (DIRT_HEIGHT-1, int(self.bounds[1]/2.))

        # CREATE STARTING CELLS.
        cell = self.create_cell(coords=self.start)

    def step(self, *args, **kwargs):
        """Override step to calcualte light input after each step.
        """
        super(Simulation, self).step()
        self._filter_unconnected()

    def create_input(self, cell):
        is_underground = cell.userData['coords'][0] < DIRT_HEIGHT
        return [int(is_underground)]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def _filter_unconnected(self):
        seen = set()
        front = set()

        # All cells underground.
        for coord in self.hmap.coords():
            if coord[0] < DIRT_HEIGHT and self.hmap[coord]:
                front.add(coord)

        while len(front) > 0:
            next_front = set()
            for (i, j) in front:
                for coords in self.hmap.neighbor_coords((i,j), filter_valid=True):
                    if self.hmap[coords]:
                        next_front.add(coords)

            seen.update(front)
            next_front = next_front.difference(seen)
            front      = next_front

        count_destroyed = 0
        for row in range(self.bounds[0]):
            for col in range(self.bounds[1]):
                if self.hmap[row][col] and (row, col) not in seen:
                    self.destroy_cell(self.hmap[row][col])
                    count_destroyed += 1

        if self.verbose:
            print("Filtered %i unconnected"%count_destroyed)

    def fitness(self):
        if len(self.cells) == 0:
            return 0

        MAX_LIGHT = float(self.bounds[1])

        light_fitness = 0

        water_map = self.module_simulations[3].water_map
        for cell in self.cells:
            # Cells without water cannot colelct light.
            if water_map[cell.userData['coords']]:
                light_fitness += cell.userData['light']

        light_fitness /= MAX_LIGHT

        weight_fitness = 1-(len(self.cells)/float(self.bounds[0]*self.bounds[1]))

        fos = self.module_simulations[4].truss.fos_total
        fos_fitness = (math.atan((fos - 1) * 10) / math.pi) + 0.5

        # if fos < 1:
        #     return 0
        return light_fitness * fos_fitness

    def _draw_hex(self, coord, hexview):
        if self.hmap[coord]:
            if coord[0] >= DIRT_HEIGHT:
                hexview.fill((0, 200, 0))
            else:
                hexview.fill((118, 57, 49))
            hexview.border()
        else:
            if coord[0] >= DIRT_HEIGHT:
                pass
                # hexview.fill((255, 255, 255))
            else:
                hexview.fill((210, 166, 121))

    def render(self, surface):
        draw_hex_map(surface, self.hmap, self._draw_hex)
        draw_text(surface, (2, 10), "Num cells:%i"%len(self.cells))
        draw_text(surface, (2, 30), "Fitness :%f"%self.fitness())
