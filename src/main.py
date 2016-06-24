import os
import sys
import pickle
import argparse
from os import path

from neat import nn, parallel, population
from neat.config import Config
from cellGenome import CellGenome

# simulation_dimensions = (800,800)
# import numpy as np
import experiments

def init_output(dirname):
  if path.exists(dirname):
    erase = raw_input('Delete existing out folder? (y/n) :')
    if erase.lower() in ['y', 'yes']:
      os.system("rm -rf " + dirname)
    else:
      sys.exit(0)
  os.makedirs(dirname)

def main(args):
  # Change the Genome used.
  local_dir = path.dirname(__file__)
  config    = Config(path.join(local_dir, 'config.txt'))
  config.genotype = CellGenome

  # Create a population.
  pop = population.Population(config)

  # Initialize output directory.
  init_output(args.out)

  # Custom experiment with fitness function.
  experiment = experiments.FixedSize()
  def evaluate_genomes(genomes):
    for g in genomes:
      g.fitness = experiment.evaluate_genome(g)

  # Run single or multi core.
  if args.cores > 1:
    pe  = parallel.ParallelEvaluator(args.cores, experiment.evaluate_genome)
    pop.run(pe.evaluate, args.generations)
  else:
    pop.run(evaluate_genomes, args.generations)

  # Save the winner.
  with open(path.join(args.out,'population.p'), 'wb') as f:
    pickle.dump(pop, f)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--out', help='Output directory', required=True)
  parser.add_argument('-g', '--generations', help='', required=True, type=int)
  parser.add_argument('-c', '--cores', help='', required=False, default=None, type=int)
  args = parser.parse_args()
  main(args)
