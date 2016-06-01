import os
import sys
import pickle
import random
import argparse
from os import path
import math

from neat import nn, parallel, population
from neat.config import Config
from physics import VoronoiSpringPhysics
from simulation import Simulation
from cellGenome import CellGenome

simulation_dimensions = (800,800)

def make_array(w, h):
  return [[0 for x in range(w)] for y in range(h)]

def init_output(dirname):
  if path.exists(dirname):
    # erase = input('Delete existing out folder? (y/n) :')
    if True:#erase.lower() == 'y':
      os.system("rm -rf "+dirname)
    else:
      print('aborting.')
      return
  os.makedirs(dirname)

def fitness2(genome):
  physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                damping=0.4, timestep = .05)
  sim = Simulation(genome, physics, simulation_dimensions)
  sim.run(100)
  k = 75
  n = len(sim.cells)
  fitness = 1 - abs(n-k)
  return fitness

def fitness(genome):
  physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
                                damping=0.4, timestep = .05)
  sim = Simulation(genome, physics, simulation_dimensions)
  sim.run(100)

  n = len(sim.cells)

  if n < 10:
    return 0

  if n < 20:
    size_score = n/20.0
  else:
    size_score = 1

  minX, maxX, minY, maxY = 0,0,0,0
  for cell in sim.cells.values():
    minX = min(cell.px, minX)
    maxX = max(cell.px, maxX)
    minY = min(cell.py, minY)
    maxY = max(cell.py, maxY)

  width = maxX - minX
  height = maxY - minY
  # print width, height
  shape_score = 1.0 / (1.0 + math.exp(-(height/width - 2)))

  fitness = .3*size_score + .7*shape_score
  # for y in range(simulation_dimensions[0]):
  #   for x in range(simulation_dimensions[1]):
  #     if x < 200 or y < 200 or y > 600:
  #       target[x][y] = 1

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
  local_dir = path.dirname(__file__)
  config    = Config(path.join(local_dir, 'config.txt'))
  config.genotype = CellGenome

  init_output(args.out)
  pop = population.Population(config)

  if args.cores > 1:
    pe  = parallel.ParallelEvaluator(args.cores, evaluate_genome)
    pop.run(pe.evaluate, args.generations)
  else:
    pop.run(evaluate_genomes, args.generations)

  # Save the winner.
  print('Number of evaluations: {0:d}'.format(pop.total_evaluations))

  with open(path.join(args.out,'population.p'), 'wb') as f:
    pickle.dump(pop, f)

if __name__ == '__main__':
  # import inspect
  # print inspect.getsourcelines(fitness)

  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--out', help='Output directory', required=True)
  parser.add_argument('-g', '--generations', help='', required=True, type=int)
  parser.add_argument('-c', '--cores', help='', required=False, default=None, type=int)
  args = parser.parse_args()
  main(args)
