from neat import nn, population, statistics, visualize, parallel, ctrnn
from neat.config import Config
import pickle, os
import numpy as np
import letters
from sklearn import metrics
from simulate import simulate
from visualize_growth import plot_genome

def get_score(pred, true):
	# return metrics.accuracy_score(true.ravel(), pred.ravel())
	return metrics.roc_auc_score(true.ravel(), pred.ravel())

def get_start(genome):
	start = [int(g.value) for g in genome.attribute_genes[:2]]
	return start

def eval_fitness_letter(genome, letter=letters.R):
	net    = nn.create_feed_forward_phenotype(genome)
	output = simulate(net, letter.shape, get_start(genome))[0]
	score  = get_score(output, letter)
	return score

def main():
	num_generations = 100
	num_cores = 8

	# fitness_fun = lambda genomes: eval_fitness_letter(genomes, letter)
	pe = parallel.ParallelEvaluator(num_cores, eval_fitness_letter)
	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	config = Config(config_path)

	pop         = population.Population(config)
	pop.epoch(pe.evaluate, num_generations, plot_genome)

	# Display the most fit genome.
	print('\nBest genome:')
	winner = pop.most_fit_genomes[-1]

	plot_genome(winner, [8,8])
	plot_genome(winner, [16, 16])
	plot_genome(winner, [32, 32])
	
	visualize.plot_stats(pop)
	visualize.plot_species(pop)
	visualize.draw_net(winner, view=True)

	with open(os.path.join(local_dir, 'best_genome.p'), 'wb') as f:
		pickle.dump(winner, f)

if __name__ == '__main__':
    main()