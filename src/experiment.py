import os
from os import path
import sys
import argparse
import pickle
from pprint import pprint

from neat.parallel import ParallelEvaluator
from neat import population, visualize
from neat.config import Config
from .cellGenome import CellGenome

# class Input(object):
#     """docstring for Input"""
#     def __init__(self, name, func):
#         self.name = name
#         self.func = func

# class Output(object):
#     """docstring for OutPut"""
#     def __init__(self, name, func, type='sigmoid', binary=True):
#         self.name = name
#         self.type = type
#         self.binary = binary
#         self.func = func

#     def __str__(self):
#         return "%s, type:%s, binary:%b" % (self.name, self.type, self.binary)
#     # def __val__(str):
#     #     return "%s, type:%s, binary:%b" % (self.name, self.type, self.binary)

# class OutputCluster(object):
#     """docstring for OutPutCluster"""
#     def __init__(self, name, outputs, func):
#         self.outputs = outputs
#         self.func = func

class Experiment(object):
    def __init__(self, cores, generations, population, out_dir='./out/derp'):
        # Run options
        self.cores = cores
        self.out_dir = out_dir
        self.generations = generations
        self.population = population
        self.Simulation = None
        self.final_renderer = None

        if path.exists(out_dir):
            print('"%s" already exists'% out_dir)
            # erase = raw_input('Delete existing out folder? (y/n) :')
            if True:#erase.lower() in ['y', 'yes']:
              os.system("rm -rf " + out_dir)
            else:
              sys.exit(0)
        os.makedirs(out_dir)

    def evaluate_genome(self, genome):
        simulation = self.Simulation(genome)
        simulation.set_up()
        simulation.run()
        return simulation.fitness(simulation)

    def evaluate_genomes(self, genomes):
        for g in genomes:
          g.fitness = self.evaluate_genome(g)

    def report(self, pop, Renderer):
        winner = pop.statistics.best_genome()

        with open(path.join(self.out_dir,'winner.p'), 'wb') as f:
            pickle.dump(winner, f)

        genome_text = open(path.join(self.out_dir,'winner.txt'), 'w+')
        genome_text.write('fitness: %f\n' % winner.fitness)
        genome_text.write(str(winner))

        # Plot the evolution of the best/average fitness.
        visualize.plot_stats(pop.statistics, ylog=True,
                            filename=path.join(self.out_dir,"nn_fitness.svg"))

        # Visualizes speciation
        visualize.plot_species(pop.statistics,
                        filename=path.join(self.out_dir,"nn_speciation.svg"))

        # Visualize the best network.
        node_names = dict()
        for i, name in enumerate(winner.inputs + winner.outputs):
            node_names[i] = name

        visualize.draw_net(winner, view=False, node_names=node_names,
                        filename=path.join(self.out_dir,"nn_winner.gv"))

        if Renderer:
            renderer = Renderer()
            simulation = self.Simulation(winner)
            simulation.verbose = True
            simulation.set_up()
            simulation.run(renderer)
            renderer.hold()

        print('Report finished.')

    def run(self, Simulation, Renderer):
        self.Simulation = Simulation
        print('Starting Experiment.')
        print(pprint(vars(self)))

        # Change the Genome used.
        local_dir = path.dirname(__file__)
        config = Config(path.join(local_dir, '../config.txt'))
        config.genotype = CellGenome
        config.genome_config = Simulation.genome_config
        config.pop_size = self.population

        # Create a population.
        pop = population.Population(config)

        # Run single or multi core.
        if self.cores > 1:
            pe = ParallelEvaluator(self.cores, self.evaluate_genome)
            pop.run(pe.evaluate, self.generations)
        else:
            pop.run(self.evaluate_genomes, self.generations)
        print('Experiment finished.')
        self.report(pop, Renderer)
