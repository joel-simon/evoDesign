import os
from os import path
import sys
import argparse
import pickle
from pprint import pprint
import subprocess
from datetime import datetime
from shutil import copyfile
# import traceback
import logging
import importlib

from neat.parallel import ParallelEvaluator
from neat import population
from neat.config import Config

from src.neat_custom import ctrnn
from src.cellGenome import CellGenome
from src.views import View

logging.basicConfig(level=logging.DEBUG, filename='./debug/derp.log')

def evaluate_genome(genome):
    try:
        simulation = Simulation(genome)
        return simulation.run()

    except KeyError as e:
        print '!'*80
        print "Exception in evaluating genome. Creating Debug file."
        print '!'*80
        print
        prefix = "({:%B_%d_%Y_%H-%M})".format(datetime.now())
        logging.exception("Error in evaluate_genome")

        with open(path.join('debug', prefix+'_genome.p'), 'wb') as f2:
            pickle.dump(genome, f2)

        raise e

        # return 0

def evaluate_genomes(genomes):
    for genome in genomes:
        genome.fitness = evaluate_genome(genome)

    best = max(genomes, key=lambda genome: genome.fitness)
    simulation = Simulation(best)
    view = View(800, 800, simulation)
    simulation.run(renderer=view)

def report(pop, out_dir, experiment):
    genome = pop.statistics.best_genome()

    with open(path.join(out_dir, 'genome.p'), 'wb') as f:
        pickle.dump(genome, f)

    with open(path.join(out_dir, 'population.p'), 'wb') as f:
        pickle.dump(pop, f)

    genome_text = open(path.join(out_dir, 'genome.txt'), 'w+')
    genome_text.write('fitness: %f\n' % genome.fitness)
    genome_text.write(str(genome))

    # Visualize the best network.
    subprocess.call(['./generate_graphs.sh', out_dir])

    # Save step animation.
    os.mkdir(path.join(out_dir, 'img'))
    simulation = Simulation(genome)
    view = View(800, 800, simulation, save=path.join(out_dir, 'img'))
    simulation.verbose = True
    simulation.run(renderer=view)

    copyfile('./config.txt', path.join(out_dir, 'config.txt'))
    copyfile('./experiments/%s.py' % experiment, path.join(out_dir, '%s.py.txt' % experiment))

    print('Report finished.')

def main(cores, generations, pop_size, out_dir, experiment):
    if path.exists(out_dir):
        print('"%s" already exists'% out_dir)
        erase = raw_input('Delete existing out folder? (y/n) :')
        if erase.lower() in ['y', 'yes']:
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
    config.genome_config = genome_config
    config.pop_size = pop_size
    # config.node_gene_type = ctrnn.CTNodeGene

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
    report(pop, out_dir, experiment)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', help='Output directory', default='')
    parser.add_argument('-g', '--generations', default=100, type=int)
    parser.add_argument('-p', '--population', default=100, type=int)
    parser.add_argument('-c', '--cores', default=1, type=int)
    parser.add_argument('-e', '--experiment', required=True)
    parser.add_argument('-s', '--simulation', default='Simulation')

    args = parser.parse_args()
    default_dir = './out/'+args.experiment+"({:%B_%d_%Y_%H-%M})".format(datetime.now())

    try:
        mod = importlib.import_module('experiments.%s' % args.experiment)
    except ImportError, e:
        print('ERR: Cannot find experiment "./experiments/%s"' % args.experiment)
        print(e)
        sys.exit(0)

    try:
        global Simulation, genome_config
        Simulation = getattr(mod, args.simulation)
        genome_config = getattr(mod, 'genome_config')
    except AttributeError:
        print('ERR: Cannot find class "Simulation" in module.')
        sys.exit(0)

    if args.out == '':
        out = default_dir
    else:
        out = args.out
    main(args.cores, args.generations, args.population, out, args.experiment)
