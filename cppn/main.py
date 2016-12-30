from __future__ import print_function
import neat
import os
import pickle
from itertools import product
from multiprocessing import Pool
from neat import population, config, visualize, parallel, nn

from src.map_utils import shape, connected_mask
from src.balance import balance_score


def create_table(genome, shape):
    net = nn.create_feed_forward_phenotype(genome)

    X, Y, Z = shape
    table = [[[0 for k in range(Z)] for j in range(Y)] for i in range(X)]
    static_cells = [] # (x, y, z) coordinates where y=0
    positions = []

    for x, y, z in product(range(shape[0]), range(shape[1]), range(shape[2])):
        _x = -1.0 + 2.0 * x / (shape[0] - 1)
        _y = -1.0 + 2.0 * y / (shape[1] - 1)
        _z = -1.0 + 2.0 * z / (shape[2] - 1)

        out = net.serial_activate([_x, _y, _z])
        has_cell = out[0] > .5
        table[x][y][z] = has_cell

        if has_cell:
            positions.append((x, y, z))
            if y == 0:
                static_cells.append((x, y, z))

    conn_mask = connected_mask(table, start=static_cells)
    return table, conn_mask

def draw(genome):
    view.clear()
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

def evaluate_all(genomes):
    for g in genomes:
        g.fitness = evaluate(g)

    # winner = max(genomes, key=lambda g:g.fitness)
    # draw(winner)

class Cell(object):
    def __init__(self, position):
        self.position = position

# import numpy as np
def evaluate(genome, shape=(8,8,8), verbose=False):
    table, connected_mask = create_table(genome, shape)
    X, Y, Z = shape

    y_max = 0
    connected_cells = []
    for x, y, z in product(range(shape[0]), range(shape[1]), range(shape[2])):
        if connected_mask[x][y][z]:
            connected_cells.append(Cell((x, y, z)))
            y_max = max(y_max, y)

    top_covereage = 0

    for x, z in product(range(shape[0]), range(shape[2])):
        top_covereage += connected_mask[x][-1][z]

    weight_fitness = 1 - (len(connected_cells) / float(X*Y*Z))

    height_fitness = y_max / float(Y-1)

    cover_fitness = top_covereage / float(X * Z)

    balance_fitness = balance_score(connected_cells, connected_mask)

    total_fitness = ((.1*height_fitness+.9*cover_fitness) * weight_fitness * balance_fitness) ** (1/3.0)

    if verbose:
        print('#'*80)
        print('cover_fitness', cover_fitness)
        print('weight_fitness', weight_fitness)
        print('balance_fitness', balance_fitness)
        print('\ntotal_fitness', total_fitness)
        print('#'*80)

    return total_fitness

def main():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    pop = population.Population(config_path)
    pop.run(evaluate_all, 1000)

    winner = pop.statistics.best_genome()
    table = create_table(winner, (8,8,8))[0]
    pickle.dump(winner, open('cppn/winner_genome.p', 'wb'))
    pickle.dump(pop, open('cppn/winner_population.p', 'wb'))

if __name__ == '__main__':
    main()
