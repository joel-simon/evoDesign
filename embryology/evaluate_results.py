import sys
import pickle
import experiments

def main(path):
	experiment_8x8  = experiments.SurfaceArea((8,8))
	experiment_4x12 = experiments.SurfaceArea((4,12))
	experiment_12x4 = experiments.SurfaceArea((12,4))

	best_genomes = pickle.load(open(path, 'rb'), encoding='latin1')
	for genome in best_genomes:
		print(experiment_8x8.fitness(genome))
		print(experiment_4x12.fitness(genome))
		print(experiment_12x4.fitness(genome))
		print()

if __name__ == '__main__':
	main(sys.argv[1])
