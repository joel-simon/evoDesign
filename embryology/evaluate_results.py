import sys
import pickle
import experiments

def main(path):
	to_run = [
		experiments.SurfaceArea((24,24)),
		experiments.SurfaceArea((12,24)),
		experiments.SurfaceArea((24,12)),
		# experiments.SurfaceArea((12,4)),
		# experiments.SurfaceArea((16,16)),
	]

	best_genomes = pickle.load(open(path, 'rb'), encoding='latin1')
	for genome in best_genomes:
		print()
		print(genome.ID, genome.fitness)
		for e in to_run:
			print(e.shape, e.fitness(genome))
		print()

if __name__ == '__main__':
	main(sys.argv[1])
