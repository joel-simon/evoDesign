import math
from src.hexSimulation import HexSimulation
from src.hexmap import Map
from src.classification import f1_score, joel_score, precision_recall
from src.gene_modules import signals

def angular_distance(theta_1, theta_2, mod=2*math.pi):
    difference = abs(theta_1 % mod - theta_2 % mod)
    return min(difference, mod - difference)

genome_config = {
    'gene_modules' : [
        { 'gene':signals.Signal4, 'prob_add':.2, 'max_genes':5 }],
    'inputs': [
        'neighbor_t', 'neighbor_tr',
        'neighbor_br', 'neighbor_b',
        'neighbor_bl', 'neighbor_tl'],
    'outputs': [
        ('apoptosis', 'sigmoid'),
        ('divide', 'sigmoid'),
        ('axis_cos', 'identity'),
        ('axis_sin', 'identity'),
    ]
}

class Shapes(HexSimulation):
    """docstring for Shapes"""
    def __init__(self, genome):
        super(Shapes, self).__init__(genome, max_steps=100, bounds=(8, 8),
                                     break_on_repeat=True)
        # Create starting cells
        self.start = (0, 0)
        cell = self.create_cell(coords=self.start)

        # Target to be scored against.
        self.target = self.create_target()
        self.hex_angles = map(math.radians, [30, 90, 150, 210, 270, 330])

    def create_inputs(self, cell):
        coords = cell.userData['coords']
        inputs = list(map(bool, self.hmap.neighbors(coords)))

        assert(len(inputs) == len(genome_config['inputs']))
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

    def fitness(self):
        true = sum(self.target,[])
        pred = sum(self.hmap, [])
        return joel_score(true, pred)

class E(Shapes):
    def create_target(self):
        target = Map(self.bounds, 0)
        for i in range(self.bounds[1]):
            target[self.bounds[0]-1][i] = 1
            target[self.bounds[0]-2][i] = 1

        for i in range(self.bounds[1]):
            target[0][i] = 1
            target[1][i] = 1

        for i in range(self.bounds[1]):
            target[self.bounds[0]/2][i] = 1
            target[self.bounds[0]/2 -1][i] = 1

        for i in range(self.bounds[0]):
            target[i][0] = 1
            target[i][1] = 1
        return target

class O(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(self.bounds[1]):
            target[(0, i)] = 1
            target[(1, i)] = 1
            target[(6, i)] = 1
            target[(7, i)] = 1

            target[(i, 0)] = 1
            target[(i, 1)] = 1
            target[(i, 6)] = 1
            target[(i, 7)] = 1
        return target

class R(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(8):
            target[(2, i)] = 1
            target[(3, i)] = 1
            target[(6, i)] = 1
            target[(7, i)] = 1
            target[(i, 0)] = 1
            target[(i, 1)] = 1
            target[(i, 6)] = 1
            target[(i, 7)] = 1

        target[(1, 5)] = 1
        target[(2, 7)] = 0

        return target

class Y(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(6):
            target[(i, 3)] = 1
            target[(i, 4)] = 1

        for coords in [(7, 0), (6, 1), (6, 2), (6, 0), (5, 1), (5, 2), (6, 7),
                        (6, 6), (5, 5), (7, 7), (7, 6), (6, 5), (6, 4)]:
            target[coords] = 1
        return target

class X(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(8):
            target[(i, i)] = 1
            target[(i, 7-i)] = 1
        target[(0,1)] = 1
        target[(2,3)] = 1
        target[(2,6)] = 1
        target[(6,2)] = 1
        target[(7,6)] = 1
        target[(5,4)] = 1
        return target

class stripes(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(self.bounds[0]):
            for j in range(0, self.bounds[1], 2):
                target[(i, j)] = 1
        return target

class loops(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for r in range(self.bounds[0]):
            for c in range(self.bounds[1]):
                if target.distance((0,0), (r,c))%2 == 1:
                    target[(r, c)] = 1
        return target

class dots(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(0, 8, 3):
            for j in range(0, 8, 1):
                target[(i+j%2, j)] = 1
        return target

class checkerboard(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(0, 8, 3):
            for j in range(0, 8, 1):
                neighbors = target.neighbor_coords((i+j%2, j), filter_valid=True)
                for coords in neighbors:
                    target[coords] = 1
        return target

class circles(Shapes):
    def create_target(self):
        target = Map(self.bounds)
        for center in [(1,1), (6,1), (1, 6), (6,6)]:
            for coords in target.neighbor_coords(center, filter_valid=True):
                target[coords] = 1
        return target
