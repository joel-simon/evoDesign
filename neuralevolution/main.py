from neat import nn, population, statistics, visualize, parallel
import pickle, os
import numpy as np
import letters
from sklearn import metrics
from simulate import simulate



def get_score(a, b):
	return metrics.accuracy_score(b.ravel(), a.ravel(), normalize = True)
	# return metrics.f1_score(a.ravel(), b.ravel())

def eval_fitness_letter(genome, letter=letters.L):
	net = nn.create_feed_forward_phenotype(genome)
	n_averages = 1
	outputs = [ simulate(net, letter.shape) for _ in range(n_averages) ]
	score = np.mean([ get_score(o, letter) for o in outputs ])
	return score

def log_best(genome):
	net    = nn.create_feed_forward_phenotype(genome)
	output = simulate(net, [8,8])
	letters.pretty_print(output)

def main():
	num_generations = 50
	num_cores = 8

	# fitness_fun = lambda genomes: eval_fitness_letter(genomes, letter)
	pe = parallel.ParallelEvaluator(num_cores, eval_fitness_letter)
	local_dir   = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'main_config')
	pop         = population.Population(config_path)
	pop.epoch(pe.evaluate, num_generations, log_best)

	# Display the most fit genome.
	print('\nBest genome:')
	winner = pop.most_fit_genomes[-1]
	winner_net = nn.create_feed_forward_phenotype(winner)
	letters.pretty_print(simulate(winner_net, [8,8]))
	letters.pretty_print(simulate(winner_net, [16, 16]))
	letters.pretty_print(simulate(winner_net, [32, 32]))
	
	visualize.plot_stats(pop)
	visualize.plot_species(pop)
	visualize.draw_net(winner, view=True)

	with open(os.path.join(local_dir, 'best_genome.p'), 'wb') as f:
		pickle.dump(winner, f)

if __name__ == '__main__':
    main()