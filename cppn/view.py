from __future__ import print_function
import neat
import os
import pickle

from itertools import product

from src.map_utils import shape, connected_mask
from src.balance import balance_score
from src.views.viewer import Viewer

from .main import create_table, evaluate

view = Viewer((8, 8, 8))

genome = pickle.load(open('/Users/joelsimon/Projects/evoDesign/cppn/winner_genome.p'))

print(evaluate(genome, verbose=True))
# print('Fitness:', genome.fitness)

view.start_draw()
table, conn_mask = create_table(genome, (8,8,8))

for x, y, z in product(range(8), range(8), range(8)):
    if table[x][y][z]:
        if conn_mask[x][y][z]:
            view.draw_cube(x, y, z, (.9, .9, .9, 1))
        else:
            view.draw_cube(x, y, z, (.5, .5, .5, .2), border=False)

view.end_draw()
view.main_loop()
