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
	
	# original_experiment = 
	to_run = [
		# experiments.Tree((24,24)),
		experiments.Tree((12, 12)),
		experiments.Tree((12,24)),
		experiments.Tree((24,12))
	]
	
	for rank, genome in enumerate(best_genomes[:5]):
		
		neat_visualize.draw_net(genome, view = False, filename='network'+str(rank))
		print()
		# print(genome.ID, genome.fitness)
		for e in to_run:
			visualize.make_gif(screen, genome, e, str(rank)+str(e.shape))
			print(e.shape, e.fitness(genome))
		print()

if __name__ == '__main__':
	main(sys.argv[1])
