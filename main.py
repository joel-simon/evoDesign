import os
from os import path
import sys
import argparse
import pickle
from pprint import pprint
import subprocess
from datetime import datetime
from shutil import copyfile

import logging
import importlib

from neat.parallel import ParallelEvaluator
from neat import population

from src.neat_custom.config import Config as NeatConfig
from src.neat_custom import ctrnn
from src.cellGenome import CellGenome
from src.views import View

class Experiment(object):
    def __init__(self, simulation, genome_config, neat_config):
        self.simulation = simulation
        self.genome_config = genome_config
        self.neat_config = neat_config

        neat_config.genotype = CellGenome
        neat_config.genome_config = genome_config
        # neat_config.node_gene_type = ctrnn.CTNodeGene

    def evaluate_genome(self, genome):
        sim = self.simulation(genome)
        return sim.run()

    def evaluate_genomes(self, genomes):
        for genome in genomes:
            genome.fitness = self.evaluate_genome(genome)

        best = max(genomes, key=lambda genome: genome.fitness)
        sim = self.simulation(best)
        view = View(800, 800, sim)
        sim.run(renderer=view)

    def report(self, pop, out_dir, config_path):
        assert not path.exists(out_dir)
        os.makedirs(out_dir)

        genome = pop.statistics.best_genome()

        with open(path.join(out_dir, 'genome.p'), 'wb') as genome_out:
            pickle.dump(genome, genome_out)

        with open(path.join(out_dir, 'population.p'), 'wb') as population_out:
            pickle.dump(pop, population_out)

        genome_text = open(path.join(out_dir, 'genome.txt'), 'w+')
        genome_text.write('fitness: %f\n' % genome.fitness)
        genome_text.write(str(genome))

        # Visualize the best network.
        subprocess.call(['./generate_graphs.sh', out_dir])

        # Save step animation.
        os.mkdir(path.join(out_dir, 'img'))
        simulation = self.simulation(genome)
        view = View(800, 800, simulation, save=path.join(out_dir, 'img'))
        simulation.verbose = True
        simulation.run(renderer=view)

        copyfile(config_path, path.join(out_dir, 'config.txt'))
        # copyfile('./experiments/%s.py' % experiment, path.join(out_dir, '%s.py.txt' % experiment))

        print('Report finished.')

    def run(self, cores, generations, pop_size):
        assert isinstance(cores, int)
        assert isinstance(generations, int)

        # print "Running experiment"
        # print "\tcores: %i" % cores
        # print "\tgenerations: %i" % generations
        # print "\tgenerations: %i" % generations
        self.neat_config.pop_size = pop_size
        pop = population.Population(self.neat_config)
        if cores > 1:
            pe = ParallelEvaluator(cores, self.evaluate_genome)
            pop.run(pe.evaluate, generations)
        else:
            pop.run(self.evaluate_genomes, generations)
        return pop

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', help='Output directory', default='')
    parser.add_argument('-g', '--generations', default=100, type=int)
    parser.add_argument('-p', '--population', default=100, type=int)
    parser.add_argument('-c', '--cores', default=1, type=int)
    parser.add_argument('-e', '--experiment', required=True)
    parser.add_argument('-s', '--simulation', default='Simulation')
    parser.add_argument('--config', help='NEAT config file', required=True)

    args = parser.parse_args()

    if args.out == '':
        args.out = './out/'+args.experiment+"({:%B_%d_%Y_%H-%M})".format(datetime.now())

    mod = importlib.import_module('experiments.%s' % args.experiment)
    simulation = getattr(mod, args.simulation)
    genome_config = getattr(mod, 'genome_config')

    if path.exists(args.out):
        print('"%s" already exists'% args.out)
        sys.exit(0)

    run_config = {'generations': args.generations, 'cores': args.cores, 'pop_size':args.population}
    neat_config = NeatConfig(args.config)
    neat_config.pop_size = args.population

    experiment = Experiment(simulation, genome_config, neat_config)
    pop = experiment.run(**run_config)
    experiment.report(pop, args.out, args.config)
