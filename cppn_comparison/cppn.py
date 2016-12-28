import neat
import os
import pickle
# import numpy as np

from multiprocessing import Pool
from neat import population, config, visualize, parallel, nn

from src.map_utils import shape, connected_mask
from src.balance import balance_score
# from src.view.viewer import Viewer

def create_table(genome, shape):
    net = nn.create_feed_forward_phenotype(genome)

    X, Y, Z = shape
    table = [[[0 for k in xrange(Z)] for j in xrange(Y)] for i in xrange(X)]
    positions = []

    for x in range(shape[0]):
        for y in range(shape[1]):
            for z in range(shape[2]):
                out = net.serial_activate([x, y, z])
                table[x][y][z] = (out[0] > .5)
                if out[0] > .5:
                    positions.append((x, y, z))
    return table, positions

def evaluate_all(genomes):
    for g in genomes:
        g.fitness = evaluate(g)
    # best = max(genomes, key = lambda g: g.fitness)
    # best_table = c/\reate_table(best, (8,8,8))


class Cell(object):
    def __init__(self, position):
        self.position = position

# import numpy as np
def evaluate(genome, shape=(8,8,8),verbose=False):
    table, positions = create_table(genome, shape)
    X, Y, Z = shape

    static_cells = [p for p in positions if p[1] == 0]
    connected_array = connected_mask(table, start=static_cells)
    connected_cells = [ ]

    for p in positions:
        x, y, z = p
        if connected_array[x][y][z]:
            connected_cells.append(Cell(p))

    y_max = 0
    top_covereage = 0
    for cell in connected_cells:
        y_max = max(y_max, cell.position[1])
        top_covereage += (cell.position[1] == Y-1)

    weight_fitness = 1 - (len(connected_cells) / float(X*Y*Z))

    height_fitness = y_max / float(Y)

    cover_fitness = top_covereage / float(X * Z)

    balance_fitness = balance_score(connected_cells, connected_array)

    total_fitness = .1*height_fitness + .9*cover_fitness
    total_fitness *= .4*weight_fitness + .6
    total_fitness *= balance_fitness


    if verbose:
        print 'cover_fitness', cover_fitness
        print 'weight_fitness', weight_fitness
        print 'balance_fitness', balance_fitness
        print 'total_fitness', total_fitness

    return total_fitness

def main():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    # Use a pool of four workers to evaluate fitness in parallel.
    # pe = parallel.ParallelEvaluator(1, fitness)
    pop = population.Population(config_path)
    pop.run(evaluate_all, 200)

    winner = pop.statistics.best_genome()
    table = create_table(winner, (8,8,8))[0]
    pickle.dump(winner, open('cppn_winner_genome.p', 'wb'))
    pickle.dump(table, open('cppn_winner_table.p', 'wb'))
    # Visualize the winner network and plot statistics.
    # visualize.plot_stats(pop.statistics)
    # visualize.plot_species(pop.statistics)
    # visualize.draw_net(winner, view=True)

main()
