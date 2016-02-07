import sys
import pickle
import experiments

def main(path):
	experiment_4x12 = experiments.SurfaceArea((12,12))
	experiment_12x4 = experiments.SurfaceArea((12,12))
	
	best_genomes = pickle.load(open(path, 'rb'), encoding='latin1')
	for genome in best_genomes:
		print(experiment.fitness(genome), genome.fitness)

if __name__ == '__main__':
	main(sys.argv[1])
