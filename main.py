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
from src.neat_custom import ctrnn
from src.cellGenome import CellGenome
import inspect
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
    best = max(genomes, key=lambda g:g.fitness)
    if Renderer:
        renderer = Renderer()
        simulation = Simulation(best)
        simulation.run(renderer)

def report(pop, out_dir, experiment):
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
        simulation.run(renderer)

    # with open (path.join(out_dir,'simulation.p'), 'w') as f:
    #     inspect.getsourcelines(Simulation)
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
    config.node_gene_type = ctrnn.CTNodeGene

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
