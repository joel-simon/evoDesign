from os.path import join
import sys
import os
import argparse
import pickle

from src.simulation import Simulation
from src.box2DPhysics import Box2DPhysicsRender

def main(args):
  path = args.dir
  with open(join(path, 'population.p'), 'rb') as f:
    pop = pickle.load(f)

  best_genome = pop.statistics.best_genome()
  physics = Box2DPhysicsRender(verbose=True, max_steps=999)

  sim = Simulation(best_genome, physics, max_steps=100, verbose=True)
  sim.create_cell(position=(0, 1), size=[1, 1])
  sim.run()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('dir', help='Input directory')
  parser.add_argument('--save')
  args = parser.parse_args()
  main(args)
