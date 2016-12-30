import os
from os import path
import pickle
import subprocess
from shutil import copyfile
from neat import population

from src.neat_custom.parallel import ParallelEvaluator
from src.neat_custom.config import Config as NeatConfig
from src.neat_custom import ctrnn
from src.cellGenome import CellGenome
from src import export

from src.views.viewer import Viewer

class Experiment(object):
    def __init__(self, simulation, neat_config_path, modules, params):
        self.simulation = simulation

        self.neat_config_path = neat_config_path
        self.neat_config = NeatConfig(neat_config_path)
        self.neat_config.genotype = CellGenome
        self.neat_config.genome_config = {
            'modules': modules,
            'inputs': simulation.inputs,
            'outputs': simulation.outputs
        }

        self.simulation_params = params
        self.population = None

        self.viewer = Viewer(bounds=(8,8,8))

    def evaluate_genome(self, genome):
        fitness = 1
        for simulation_params in self.simulation_params:
            sim = self.simulation(genome, **simulation_params)
            sim.run()
            fitness *= sim.max_fitness
        return fitness

    def evaluate_genomes(self, genomes):
        for genome in genomes:
            genome.fitness = self.evaluate_genome(genome)

    #     if self.population.generation % 2 == 0 and self.population.generation > 0:
    #         genome = max(genomes, key= lambda g: g.fitness)
    #         sim = self.simulation(genome, **self.simulation_params[0])
    #         sim.run()
    #         max_steps = sim.max_fitness_steps
    #         sim = self.simulation(genome, **self.simulation_params[0])
    #         sim.verbose = False
    #         sim.max_steps = max_steps + 1
    #         sim.run(viewer=None)
    #         sim.render_all(self.viewer)
    #         self.viewer.main_loop()

    def report(self, out_dir):
        assert not path.exists(out_dir)

        if self.population is None:
            raise ValueError()

        os.makedirs(out_dir)
        genome = self.population.statistics.best_genome()

        with open(path.join(out_dir, 'genome.p'), 'wb') as genome_out:
            pickle.dump(genome, genome_out)

        with open(path.join(out_dir, 'population.p'), 'wb') as population_out:
            pickle.dump(self.population, population_out)

        with open(path.join(out_dir, 'params.p'), 'wb') as params_out:
            pickle.dump(self.simulation_params, params_out)

        # with open(path.join(out_dir, 'simulation.p'), 'wb') as sim_out:
        #     pickle.dump(self.simulation, sim_out)


        genome_text = open(path.join(out_dir, 'genome.txt'), 'w+')
        genome_text.write('fitness: %f\n' % genome.fitness)
        genome_text.write(str(genome))

        # Visualize the best network.
        #

        with open(path.join(out_dir, 'report.txt'), 'w') as report:
            report.write('# BAUPLAN report.\n')

            for i, params in enumerate(self.simulation_params):
                sim = self.simulation(genome, **params)
                sim.run()
                max_steps = sim.max_fitness_steps
                sim.reset()
                # print('max_steps:', max_steps)

                sim.max_steps = max_steps + 1
                sim.verbose = True
                sim.run()
                sim.render_all(self.viewer)

                # Turn on
                self.viewer.main_loop()

                file_name = path.join(out_dir, 'final_obj_%i.obj' % i)
                meta_data = 'params #%i: %s' % (i, str(params))

                sim.save_all(out_dir)

                report.write('params #%i:\n' % i)
                report.write('\t%s\n' % str(params))
                report.write('\tfitness: %f\n' % sim.max_fitness)
                report.write('\tsteps_taken: %i\n' % sim.max_fitness_steps)

        copyfile(self.neat_config_path, path.join(out_dir, 'config.txt'))

        # copyfile('./experiments/%s.py' % experiment, path.join(out_dir, '%s.py.txt' % experiment))
        subprocess.call(['./generate_graphs.sh', out_dir])
        print('Report finished.')

    def run(self, cores, generations, pop_size):
        print("Running experiment")
        print("\tcores: %i" % cores)
        print("\tpop_size: %i" % pop_size)
        print("\tgenerations: %i" % generations)

        self.neat_config.pop_size = pop_size
        self.population = population.Population(self.neat_config)

        # pop.add_reporter(Reporter3D(self.simulation))

        if cores > 1:
            pe = ParallelEvaluator(cores, self.evaluate_genome)
            self.population.run(pe.evaluate, generations)
        else:
            self.population.run(self.evaluate_genomes, generations)

