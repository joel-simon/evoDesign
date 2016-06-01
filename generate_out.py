import pickle
from neat import visualize
import sys
from os.path import join
from main import fitness
import matplotlib.pyplot as plt
from multiprocessing import Pool
from itertools import repeat

def plot_scores(genome, filename, n=10, view=True):
  pool = Pool()
  fitnesses = pool.map(fitness, repeat(genome, n))
  plt.hist(fitnesses)
  plt.title("Score Histogram for n=%i" % n)
  plt.savefig(filename)
  if view:
    plt.show()
  print fitnesses
  plt.close()

def main(dirname):
  pop = pickle.load(open(join(dirname, 'population.p')))

  winner = pop.statistics.best_genome()

  genome_text = open(join(dirname,'genome.txt'), 'w+')
  genome_text.write('fitness: %f\n' % winner.fitness)
  genome_text.write(str(winner))

  # Plot the evolution of the best/average fitness.
  visualize.plot_stats(pop.statistics, ylog=True,
                        filename=join(dirname,"nn_fitness.svg"))

  # Visualizes speciation
  visualize.plot_species(pop.statistics,
                          filename=join(dirname,"nn_speciation.svg"))

  # Visualize the best network.
  node_names = dict()
  for i, name in enumerate(winner.inputs + winner.outputs):
    node_names[i] = name

  visualize.draw_net(winner, view=True, node_names=node_names,
                    filename=join(dirname,"nn_winner.gv"))

  # plot_scores(winner, filename=join(dirname, 'scores.png'), n=100)
  # visualize.draw_net(winner, view=True, filename="nn_winner-enabled.gv", show_disabled=False)
  # visualize.draw_net(winner, view=True, filename="nn_winner-enabled-pruned.gv", show_disabled=False, prune_unused=True)

  print('Complete.')

if __name__ == '__main__':
  if len(sys.argv) == 1:
    main('./out')
  else:
    main(sys.argv[1])
