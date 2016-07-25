import os
from os import path
import sys
import argparse
import pickle
from pprint import pprint
import subprocess
from datetime import datetime
from neat.parallel import ParallelEvaluator
from neat import population#, visualize
from neat.config import Config
from src.cellGenome import CellGenome

import importlib

from src.hexRenderer import HexRenderer as Renderer

from shutil import copyfile

def evaluate_genome(genome):
    simulation = Simulation(genome)
    return simulation.run()
    # return simulation.fitness(simulation)

def evaluate_genomes(genomes):
    for g in genomes:
        g.fitness = evaluate_genome(g)

def report(pop, out_dir):
    winner = pop.statistics.best_genome()

    with open(path.join(out_dir,'winner.p'), 'wb') as f:
        pickle.dump(winner, f)

    with open(path.join(out_dir,'population.p'), 'wb') as f:
        pickle.dump(pop, f)

    genome_text = open(path.join(out_dir,'winner.txt'), 'w+')
    genome_text.write('fitness: %f\n' % winner.fitness)
    genome_text.write(str(winner))

    # Visualize the best network.
    subprocess.call(['./generate_graphs.sh', out_dir])

    if Renderer:
        os.mkdir(path.join(out_dir, 'temp'))
        renderer = Renderer(save=path.join(out_dir, 'temp'))
        simulation = Simulation(winner)
        simulation.verbose = True
        simulation.set_up()
        simulation.run(renderer)

    copyfile('./fixedSize.py', path.join(out_dir, 'fixedSize.py'))
    copyfile('./config.txt', path.join(out_dir, 'fixedSize.txt'))

    print('Report finished.')

def main(cores, generations, pop_size, out_dir):
    if path.exists(out_dir):
        print('"%s" already exists'% out_dir)
        # erase = raw_input('Delete existing out folder? (y/n) :')
        if True:#erase.lower() in ['y', 'yes']:
          os.system("rm -rf " + out_dir)
        else:
          sys.exit(0)

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
    os.makedirs(out_dir)
    report(pop, out_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    default_dir = './out/'+"{:%B_%d_%Y_%H-%M}".format(datetime.now())
    parser.add_argument('-o', '--out', help='Output directory', default=default_dir)
    parser.add_argument('-g', '--generations', help='', default=50, type=int)
    parser.add_argument('-p', '--population', help='', default=100, type=int)
    parser.add_argument('-c', '--cores', help='', default=1, type=int)
    parser.add_argument('-E', '--experiment', help='', required=True)

    args = parser.parse_args()

    try:
        mod = importlib.import_module('experiments.%s' % args.experiment)
    except ImportError:
        print('ERR: Cannot find experiment "./experiments/%s"' % args.experiment)
        sys.exit(0)

    try:
        global Simulation
        Simulation = getattr(mod, 'Simulation')
    except AttributeError:
        print('ERR: Cannot find class "Simulation" in module.')
        sys.exit(0)

    main(args.cores, args.generations, args.population, args.out)
