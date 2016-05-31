import os
import sys
import pickle

from neat import nn, parallel, population
from neat.config import Config
from physics import VoronoiSpringPhysics
from simulation import Simulation
from cellGenome import CellGenome
from Vector import Vector
import random

simulation_dimensions = (800,800)

def init_output():
  if os.path.exists('out'):
    # erase = input('Delete existing out folder? (y/n) :')
    if True:#erase.lower() == 'y':
      os.system("rm -rf out")
    else:
      print('aborting.')
      return
  os.makedirs('out')

def fitness(genome):
  physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                damping=0.4, timestep = .05)
  sim = Simulation(genome, physics, simulation_dimensions)
  sim.run(80)

  k = 75
  n = len(sim.cells)
  fitness = 1 - abs(n-k)
  return fitness

def evaluate_genome(genome, n_avgs=1):
  fitnesses = []
  for i in range(n_avgs):   
    fitnesses.append(fitness(genome))

  return sum(fitnesses)/float(n_avgs)

def evaluate_genomes(genomes):
  for g in genomes:
    g.fitness = evaluate_genome(g)

def main(args):
  generations = int(args[0])

  local_dir = os.path.dirname(__file__)
  config    = Config(os.path.join(local_dir, 'config.txt'))
  config.genotype = CellGenome

  cores = 1

  init_output()
  pop = population.Population(config)

  if cores > 1:
    pe  = parallel.ParallelEvaluator(cores, evaluate_genome)
    pop.run(pe.evaluate, generations)
  else:
    pop.run(evaluate_genomes, generations)

  # Save the winner.
  print('Number of evaluations: {0:d}'.format(pop.total_evaluations))
  # winner = pop.statistics.best_genome()
  # with open('out/nn_winner_genome', 'wb') as f:
  #   pickle.dump(winner, f)

  with open('out/population.p', 'wb') as f:
    pickle.dump(pop, f)

if __name__ == '__main__':
  main(sys.argv[1:])
