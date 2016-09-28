import os
import math
import numpy

# from main import main
from src.hexSimulation import HexSimulation
from src.modules import signals, neighbors_distinct, divide_distinct, truss
from src.views.drawHexMap import draw_hex_map
from src.views.drawUtils import draw_text

SIMULATION_BOUNDS = (6, 12)
SIMULATION_STEPS = int(SIMULATION_BOUNDS[0] * SIMULATION_BOUNDS[1] / 2.0)

static_map = Map(SIMULATION_BOUNDS)
for row in range(0, SIMULATION_BOUNDS[0]):
    static_map[row][0] = 28
    # static_map[row][-1] = 1

# def add_loads(hmap, truss):
#     if len(truss.joints):
#         load_joint = truss.joints[0]

#         for joint in truss.joints:
#             x1 = load_joint.coordinates[0]
#             y1 = load_joint.coordinates[1]

#             if joint.coordinates[0] > x1 or (joint.coordinates[0] == x1 and joint.coordinates[1] < y1):
#                 load_joint = joint

#         load_joint.loads[1] = -5e3

# def add_loads(hmap, truss):
#     for col in range(hmap.shape[1]):
#         if hmap[-1][col]:
#             body = hmap[-1][col].userData['body']
#             body.joints['top_left'].loads[1] = -4e3
#             body.joints['top_right'].loads[1] = -4e3

def add_loads(hmap, truss):
    flag = False
    for col in reversed(range(hmap.shape[1])):
        if hmap[-1][col] and 'body' in hmap[-1][col].userData:
            body = hmap[-1][col].userData['body']
            if flag == False:
                body.joints['top_right'].loads[1] = -2e5
            else:
                body.joints['top_right'].loads[1] = 0
            flag = True
            # break

# def add_loads(hmap, truss):
#     for row in range(hmap.shape[0]):
#         if hmap[row][-1] and 'body' in hmap[row][-1].userData:
#             body = hmap[row][-1].userData['body']
#             body.joints['right'].loads[1] = -2e3
#             # body.joints['bottom_right'].loads[1] = -1e4

genome_config = {
    'modules': [
        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {}),
        (truss.TrussModule, {'static_map': static_map, 'add_loads': add_loads}),
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
        self.starts = [(self.bounds[0]-1, 0)]
        # self.starts  = [(0,0)]
        self.create_cell(self.starts[0])


    def step(self, *args, **kwargs):
        """Override step to filter unconnected
        """
        super(Simulation, self).step(*args, **kwargs)
        self._mark_unconnected()

    def create_input(self, cell):
        gradient = cell.position[1] / float(self.bounds[1])
        return [int(gradient)]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def _mark_unconnected(self):
        seen = set()
        front = set()

        for r in range(self.bounds[0]):
            coord = (r, 0)
            if self.hmap[coord]:
                front.add(coord)

        # TODO: make this search better
        while len(front) > 0:
            next_front = set()
            for (i, j) in front:
                for coords in self.hmap.neighbor_coords((i,j), filter_valid=True):
                    if self.hmap[coords]:
                        next_front.add(coords)

            seen.update(front)
            next_front = next_front.difference(seen)
            front      = next_front

        # for row in range(self.bounds[0]):
        #     for col in range(self.bounds[1]):
        #         if self.hmap[row][col]:
        #             cell = self.hmap[row][col]
        for cell in self.cells:
            if cell.position in seen:
                # print 'in'
                # cell.userData['connected'] = True
                if 'body' not in cell.userData:
                    self.module_simulations[2]._create_body(cell)
            else:
                # print 'out'
                # cell.userData['connected'] = False
                if 'body' in cell.userData:
                    cell.userData['body'].destroy()
                    del cell.userData['body']

    def fitness(self):
        fitness = 0.

        if len(self.cells) == 0:
            return fitness

        # # 25% of fitness is getting to the top
        # max_col = max(col for row, col in self.hmap.coords() if self.hmap[row][col])
        # fitness += (max_col / float(self.bounds[1] - 1)) / 4.0
        # if fitness < .25:
        #     return fitness

        # 50% is getting to right.
        max_col = 0
        for col in range(self.bounds[1]):
            if self.hmap[-1][col] and 'body' in self.hmap[-1][col].userData:
                max_col = max(max_col, col)
        fitness += (max_col / float(self.bounds[1] - 1)) / 2
        if fitness < .4:
            return fitness
        # return fitness
        # 25% is covering right
        # derp = sum(1 for row in range(self.bounds[0]) if self.hmap[row][-1] and 'body' in self.hmap[row][-1].userData)
        # fitness += (derp / float(self.hmap.shape[0])) / 4
        # if fitness < .5:
        #     return fitness
        # if derp < .9:
        #     return derp / 2.0
        # derp = max(col for col in range(0, self.hmap.shape[1]) if  self.hmap[-1][col])
        # derp /= float(self.hmap.shape[1]-1)


        # 50% is covering top
        # fitness += sum(map(bool, self.hmap[-1])) / float(self.hmap.shape[1] * 2)
        # if fitness < .50:
        #     return fitness

        # 50% is optimization
        fos = self.module_simulations[2].truss.fos_total
        fos_fitness = (math.atan((fos - 1) * 10) / math.pi) + 0.5
        # fos_fitness = 1 / (1 + math.exp(-10*(fos-1)))

        num_bodies = sum(1 for c in self.cells if 'body' in c.userData)
        weight_fitness = 1 - (len(self.cells) / float(self.bounds[0]*self.bounds[1]))
        # print fos_fitness
        # fitness += derp * fos_fitness * weight_fitness
        fitness += (fos_fitness * weight_fitness) / 2
        return fitness

    def _draw_hex(self, coord, hexview):
        if self.hmap[coord]:
            hexview.fill((100, 100, 100))
        hexview.border()

    def render(self, surface):
        draw_hex_map(surface, self.hmap, self._draw_hex)
        draw_text(surface, (2, 10), "Num cells:%i"%len(self.cells))
        draw_text(surface, (2, 30), "Fitness :%f"%self.fitness())
