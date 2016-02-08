import pickle, os, sys
import multiprocessing

from neat import population, parallel
from neat import visualize as neat_visualize
from neat import ctrnn
from neat.config import Config

import visualize
import experiments


def run_experiment(experiment, generations, parallel=False):
	local_dir = os.path.dirname(__file__)
	config = Config(os.path.join(local_dir, 'main_config'))
	# config.node_gene_type = ctrnn.CTNodeGene
	pop = population.Population(config, checkpoint_interval = None,
																						 checkpoint_generation = None)
	if parallel:
		num_cores = multiprocessing.cpu_count()
		pe = parallel.ParallelEvaluator(num_cores, experiment.fitness)
		pop.epoch(pe.evaluate, generations, experiment.draw)
	else:
		pop.epoch(experiment.fitnesses, generations, experiment.draw)

	return pop

def main(args):
	generations = int(args[0])
	parallel = False
	draw = True

	if draw:
		import pygame
		pygame.init()
		basicFont  = pygame.font.SysFont(None, 24)
		screen     = pygame.display.set_mode((800, 800))
	else:
		screen = None

	if os.path.exists('output'):
		# erase = input('Delete existing output folder? (y/n) :')
		if True:#erase == 'y':
			os.system("rm -rf output")
		else:
			print('aborting.')
			return		

	os.makedirs('output')

	experiment = experiments.SurfaceArea((12,12), screen)
	final_population = run_experiment(experiment, generations, parallel)

	best_genomes = final_population.best_genomes(5)
	winner = best_genomes[0]
	
	neat_visualize.plot_stats(final_population, filename='output/avg_fitness.svg')
	neat_visualize.plot_species(final_population, filename='output/speciation.svg')
	neat_visualize.draw_net(winner, view = False, filename='output/network')

	with open('output/best_genomes.p', 'wb') as f:
		pickle.dump(best_genomes, f)

	with open('output/best_genome.p', 'wb') as f:
		pickle.dump(winner, f)

	print()
	print('#'*80)
	print('saved best score', winner.fitness)
	print('average score', sum([bg.fitness for bg in best_genomes])/5.0)
	print('#'*80)

	for rank, genome in enumerate(best_genomes):
		visualize.make_gif(screen, genome, experiment, str(rank))

	if draw:
		experiment.draw(winner)
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

if __name__ == '__main__':
	main(sys.argv[1:])
