
import os
from os import path
import sys
import argparse
import pickle
from pprint import pprint

from neat.parallel import ParallelEvaluator
from neat import population, visualize
from neat.config import Config
from src.cellGenome import CellGenome

# import importlib
# i = importlib.import_module('src.experiment')
# from src.hexSimulation import HexSimulation as Simulation
from fixedSize import FixedSize as Simulation
# from src.hexRenderer import HexRenderer as Renderer
Renderer = None

# def plot_scores(genome, filename, n=10, view=True):
#   pool = Pool()
#   fitnesses = pool.map(fitness, repeat(genome, n))
#   plt.hist(fitnesses)
#   plt.title("Score Histogram for n=%i" % n)
#   plt.savefig(filename)
#   if view:
#     plt.show()
#   print fitnesses
#   plt.close()

def evaluate_genome(genome):
    simulation = Simulation(genome)
    simulation.set_up()
    simulation.run()
    return simulation.fitness(simulation)

def evaluate_genomes(genomes):
    for g in genomes:
        g.fitness = evaluate_genome(g)

def report(pop, out_dir):
    winner = pop.statistics.best_genome()

    with open(path.join(out_dir,'winner.p'), 'wb') as f:
        pickle.dump(winner, f)

    genome_text = open(path.join(out_dir,'winner.txt'), 'w+')
    genome_text.write('fitness: %f\n' % winner.fitness)
    genome_text.write(str(winner))

    # Plot the evolution of the best/average fitness.
    visualize.plot_stats(pop.statistics, ylog=True,
                        filename=path.join(out_dir,"nn_fitness.svg"))

    # Visualizes speciation
    visualize.plot_species(pop.statistics,
                    filename=path.join(out_dir,"nn_speciation.svg"))

    # Visualize the best network.
    node_names = dict()
    for i, name in enumerate(winner.inputs + winner.outputs):
        node_names[i] = name

    visualize.draw_net(winner, view=False, node_names=node_names,
                    filename=path.join(out_dir,"nn_winner.gv"))

    if Renderer:
        renderer = Renderer()
        simulation = Simulation(winner)
        simulation.verbose = True
        simulation.set_up()
        simulation.run(renderer)
        renderer.hold()

    print('Report finished.')

def main(cores, generations, pop_size, out_dir):
    if path.exists(out_dir):
        print('"%s" already exists'% out_dir)
        # erase = raw_input('Delete existing out folder? (y/n) :')
        if True:#erase.lower() in ['y', 'yes']:
          os.system("rm -rf " + out_dir)
        else:
          sys.exit(0)
    os.makedirs(out_dir)

    print('Starting Experiment.')
    print(pprint({
        'generations': generations,
        'pop_size':pop_size,
        'out_dir': out_dir
    }))

    # Change the Genome used.
    local_dir = path.dirname(__file__)
    config = Config(path.join(local_dir, 'config.txt'))
    config.genotype = CellGenome
    config.genome_config = Simulation.genome_config
    config.pop_size = pop_size

    # Create a population.
    pop = population.Population(config)

    # Run single or multi core.
    if cores > 1:
        pe = ParallelEvaluator(cores, evaluate_genome)
        pop.run(pe.evaluate, generations)
    else:
        pop.run(evaluate_genomes, generations)
    print('Experiment finished.')
    report(pop, out_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', help='Output directory', default='./out/derp')
    parser.add_argument('-g', '--generations', help='', default=100, type=int)
    parser.add_argument('-p', '--population', help='', default=100, type=int)
    parser.add_argument('-c', '--cores', help='', default=6, type=int)
    args = parser.parse_args()

    main(args.cores, args.generations, args.population, args.out)
