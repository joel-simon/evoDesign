import sys
import pickle
import pygame
import experiments
import visualize
from neat import visualize as neat_visualize

def main(path):
	pygame.init()
	screen = pygame.display.set_mode((800, 1000))
	best_genomes = pickle.load(open(path, 'rb'), encoding='latin1')

	original_experiment = experiments.SurfaceArea((12, 12))
	to_run = [
		experiments.SurfaceArea((24,24)),
		experiments.SurfaceArea((12,24)),
		experiments.SurfaceArea((24,12)),
	]

	visualize.make_gif(screen, best_genomes[0], experiments.SurfaceAreaBlocked((12,12)), str('blocked'))
	# for rank, genome in enumerate(best_genomes):
		
	# 	visualize.make_gif(screen, genome, original_experiment, str(rank))
	# 	# neat_visualize.draw_net(genome, view = False, filename='network'+str(rank))

	# 	print()
	# 	print(genome.ID, genome.fitness)
	# 	for e in to_run:
	# 		print(e.shape, e.fitness(genome))
	# 	print()

if __name__ == '__main__':
	main(sys.argv[1])
