import argparse
from src.hexSimulation import HexSimulation
from src.hexmap import Map
from src.classification import f1_score, joel_score, precision_recall

genome_config = {
    'gene_modules' : [
        { 'gene':signals.Signal1, 'prob_add':.2, 'max_genes':5 }],
    'inputs': [
        'neighbor_t', 'neighbor_tr',
        'neighbor_br', 'neighbor_b',
        'neighbor_bl', 'neighbor_tl',
        'light'
        ],
    'outputs': [
        ('apoptosis', 'sigmoid'),
        ('divide', 'sigmoid'),
        ('axis_cos', 'identity'),
        ('axis_sin', 'identity'),
    ]
}

class Simulation(HexSimulation):
    """docstring for Simulation"""
    def __init__(self, genome):
        super(Simulation, self).__init__(genome, max_steps=200, bounds=(13, 13))

        self.cellData = { 'light': 0 }
        self.start = (0, int(self.bounds[1]/2.))

        # CREATE STARTING CELLS.
        cell = self.create_cell(coords=self.start)

    def step(self, *args, **kwargs):
        """Override step to calcualte light input after each step.
        """
        super(Simulation, self).step(*args, **kwargs)
        self._calculate_light()

    def _calculate_light(self):
        transparancy = [1] * self.bounds[1]

        decay = 0.0

        for row in range(self.bounds[0]-1, -1, -1):
            row_value = (row+1) / float(self.bounds[0])
            for col in range(self.bounds[1]):
                cell = self.hmap[row][col]
                light = row_value * transparancy[col]
                if cell:
                    self.hmap[row][col].userData['light'] = light
                    transparancy[col] *= decay

    def create_inputs(self, cell):
        coords = cell.userData['coords']
        inputs = list(map(bool, self.hmap.neighbors(coords)))
        inputs.append(cell.userData['light'])
        # for i in range(self.genome.num_morphogens):
        #     inputs.extend(self._morphogen_inputs(cell, i))
        return inputs

    def handle_outputs(self, cell, outputs):
        assert(len(outputs) == len(genome_config['outputs']))
        coords = cell.userData['coords']

        if outputs[0] > .5:
            self.destroy_cell(cell)
            return

        if outputs[1] > .5:
            a = math.atan2(outputs[3], outputs[2])
            grow_direction = min(
                self.hex_angles,
                key=lambda b: angular_distance(b, a)
            )
            self.divide_cell(cell, self.hex_angles.index(grow_direction))



    def _filter_unconnected(self):
        seen = set()
        front = set([self.start])
        # filtered_hex_map = Map((hex_map.rows, hex_map.cols))
        while len(front) > 0:
            next_front = set()
            for (i, j) in front:
                # filtered_hex_map.values[i][j] = hex_map.values[i][j]
                # print(filter(self.hmap.neighbors()))
                for coords in self.hmap.neighbor_coords((i,j), filter_valid=True):
                    if self.hmap[coords]:
                        next_front.add(coords)
                #     if c.valid_coords()
                # neighbors = self.hmap.neighbors((i,j))
                # foo = [on for on in hex_map.occupied_neighbors((i, j)) if on != False ]
                # next_front.update(neighbors)

            seen.update(front)
            next_front = next_front.difference(seen)
            front      = next_front

        for row in range(self.bounds[0]):
            for col in range(self.bounds[1]):
                if self.hmap[row][col] and (row, col) not in seen:
                    self.cells.remove(self.hmap[row][col])
                    self.hmap[row][col] = 0
        # return filtered_hex_map

    def fitness(self):
        self._filter_unconnected()
        self._calculate_light()
        n = len(self.cells)
        # N = self.bounds[0] * self.bounds[1]
        # weight_fitness = 1 - ( self.num_cells(hexmap) / float(size) )
        if n == 0:
            return 0

        max_light = float(self.bounds[1])
        light_fitness = sum(c.userData['light'] for c in self.cells) / max_light

        size = self.bounds[0] * self.bounds[1]
        weight_fitness = 1 - ( n / float(size) )
        return (light_fitness + weight_fitness) / 2
        # return light_fitness
