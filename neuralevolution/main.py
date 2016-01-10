from neat import nn, population, statistics, visualize, parallel, ctrnn
from neat.config import Config
import pickle, os
import numpy as np
import letters
import dill
from sklearn import metrics
from simulate import simulate

num_generations = 3000
num_cores = 8
shape      = (8,8)
letter    = letters.R

def get_score(pred, true):
	# return metrics.accuracy_score(true.ravel(), pred.ravel())
	return metrics.roc_auc_score(true.ravel(), pred.ravel())

def plot_genome(genome, shape2 = shape):
	net        = nn.create_feed_forward_phenotype(genome)
	attributes = [a.value for a in genome.attribute_genes]
	output, signals, iterations_run = simulate(net, shape2, attributes)
	print(attributes)
	print(iterations_run)
	letters.pretty_print(output)
	print(signals.astype(int))

def eval_fitness_letter(genome):
	net        = nn.create_feed_forward_phenotype(genome)
	attributes = [a.value for a in genome.attribute_genes]
	output = simulate(net, shape, attributes)[0]
	score  = get_score(output, letter)
	return score

def main():
	# fitness_fun = lambda genomes: eval_fitness_letter(genomes, letter)
	pe = parallel.ParallelEvaluator(num_cores, eval_fitness_letter)
	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	config = Config(config_path)

	pop         = population.Population(config)
	pop.epoch(pe.evaluate, num_generations, plot_genome)

	# Display the most fit genome.
	print()
	print('Done')
	print('Best genome has fitness: ', pop.best_fitness_ever)
	winner = pop.best_genome_ever

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