from src.hexSimulation import HexSimulation
from src.hexmap import Map
from src.classification import balanced_accuracy_score

from src.modules import neighbors_continuous, divide_theta, neighbors_distinct, \
                        divide_distinct

from src.modules.signals.signal_3 import Signal3Module
# from src.modules.signals.signal_0 import Signal0Module
# from src.modules.signals.signal_2 import Signal2Module
from src.modules.morphogen import MorphogenModule

from src.views.drawHexMap import draw_hex_map
from src.views.drawUtils import draw_text

genome_config = {
    'modules' : [
        # (Signal3Module, {'prob_add': .0, 'prob_remove': .0,
        #                  'min_genes': 0, 'start_genes': 3, 'max_genes': 6 }),
        (MorphogenModule, {'prob_add': .0, 'prob_remove': .0,
                           'min_genes': 0, 'start_genes': 2, 'max_genes': 6 }),
        # (neighbors_continuous.NeighborModule, {}),
        # (divide_theta.DivideThetaModule, {}),

        (neighbors_distinct.NeighborModule, {}),
        (divide_distinct.DivideDistinctModule, {})
    ],

    'inputs': [],
    'outputs': [ ('apoptosis', 'sigmoid')]
}

class Shape(HexSimulation):
    """docstring for Shape"""
    def __init__(self, genome):
        super(Shape, self).__init__(genome, max_steps=32, bounds=(8, 8),
                                    break_on_repeat=True)
        # Create starting cells
        self.start = (0, 0)
        cell = self.create_cell(coords=self.start)

        # Target to be scored against.
        self.target = self.create_target()

    def create_input(self, cell):
        return []

    def handle_output(self, cell, outputs):
        if outputs[0] > .5:
            self.destroy_cell(cell)

    def fitness(self):
        true = sum(self.target,[])
        pred = sum(self.hmap, [])
        return balanced_accuracy_score(true, pred)

    def _draw_hex(self, coord, hexview):
        if self.hmap[coord]:
            hexview.fill((50, 200, 50))
            hexview.border()
        else:
            if self.target[coord]:
                hexview.fill((200, 200, 200))
        hexview.border((0,0,0), 1)

    def render(self, surface):
        draw_hex_map(surface, self.hmap, self._draw_hex)
        draw_text(surface, (2, 10), "Num cells:%i"%len(self.cells))
        draw_text(surface, (2, 30), "Fitness :%f"%self.fitness())

class E(Shape):
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

class O(Shape):
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

class R(Shape):
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

class Y(Shape):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(6):
            target[(i, 3)] = 1
            target[(i, 4)] = 1

        for coords in [(7, 0), (6, 1), (6, 2), (6, 0), (5, 1), (5, 2), (6, 7),
                        (6, 6), (5, 5), (7, 7), (7, 6), (6, 5), (6, 4)]:
            target[coords] = 1
        return target

class X(Shape):
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

class stripes(Shape):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(self.bounds[0]):
            for j in range(0, self.bounds[1], 2):
                target[(i, j)] = 1
        return target

class loops(Shape):
    def create_target(self):
        target = Map(self.bounds)
        for r in range(self.bounds[0]):
            for c in range(self.bounds[1]):
                if target.distance((0,0), (r,c))%2 == 1:
                    target[(r, c)] = 1
        return target

class dots(Shape):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(0, 8, 3):
            for j in range(0, 8, 1):
                target[(i+j%2, j)] = 1
        return target

class checkerboard(Shape):
    def create_target(self):
        target = Map(self.bounds)
        for i in range(0, 8, 3):
            for j in range(0, 8, 1):
                neighbors = target.neighbor_coords((i+j%2, j), filter_valid=True)
                for coords in neighbors:
                    target[coords] = 1
        return target

class circles(Shape):
    def create_target(self):
        target = Map(self.bounds)
        for center in [(1,1), (6,1), (1, 6), (6,6)]:
            for coords in target.neighbor_coords(center, filter_valid=True):
                target[coords] = 1
        return target
