import os
import sys
import pickle

from neat import nn, parallel, population, visualize
from neat.config import Config
from simulation import Simulation
from cellGenome import CellGenome

simulation_dimensions = (800,800)

def init_output():
  if os.path.exists('out'):
    # erase = input('Delete existing out folder? (y/n) :')
    if True:#erase == 'y':
      os.system("rm -rf out")
    else:
      print('aborting.')
      return
  os.makedirs('out')

# For multi core
def evaluate_genome(genome):
  print("Starting genome simulation")
  sim   = Simulation(genome, simulation_dimensions, draw=False)
  sim.run(10)
  n = len(sim.cells)

  if not n:
    fitness = 0.0
  else:
    fitness = sum([c.morphogens[0] for c in sim.cells.values()])/n

  print("Finished genome simulation", fitness)
  return fitness

# For single core
def evaluate_genomes(genomes):
  for g in genomes:
    g.fitness = evaluate_genome(g)

def main(args):
  generations = int(args[0])
  cores = 1
  # draw = False

  local_dir = os.path.dirname(__file__)
  config    = Config(os.path.join(local_dir, 'config.txt'))
  config.genotype = CellGenome

  init_output()
  pop = population.Population(config)
  # pe  = parallel.ParallelEvaluator(cores, evaluate_genome)
  # pop.run(pe.evaluate, generations)
  pop.run(evaluate_genomes, generations)

  # Save the winner.
  print('Number of evaluations: {0:d}'.format(pop.total_evaluations))
  winner = pop.statistics.best_genome()
  with open('out/nn_winner_genome', 'wb') as f:
    pickle.dump(winner, f)


  # Plot the evolution of the best/average fitness.
  visualize.plot_stats(pop.statistics, ylog=True, filename="out/nn_fitness.svg")
  # Visualizes speciation
  visualize.plot_species(pop.statistics, filename="out/nn_speciation.svg")
  # Visualize the best network.
  visualize.draw_net(winner, view=True, filename="out/nn_winner.gv")
  # visualize.draw_net(winner, view=True, filename="nn_winner-enabled.gv", show_disabled=False)
  # visualize.draw_net(winner, view=True, filename="nn_winner-enabled-pruned.gv", show_disabled=False, prune_unused=True)

  # if draw:
  #   # experiment.draw(winner)
  #   while True:
  #     for event in pygame.event.get():
  #       if event.type == pygame.QUIT:
  #         sys.exit()

if __name__ == '__main__':
  main(sys.argv[1:])
