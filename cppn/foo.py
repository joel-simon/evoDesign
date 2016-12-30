import argparse
import pickle
from os.path import join

from .main import evaluate

def main(args):
    path = args.dir
    best_genome = pickle.load(open(join(path, 'winner_genome.p'), 'rb'))

    sim_params = []
    for Y in range(4, 16):
        for X in range(4, 9):
            Z = 16 - X
            print((X, Y, Z), evaluate(best_genome, shape=(X, Y, Z)))
            sim_params.append({'bounds': (X, Y, Z)})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    args = parser.parse_args()
    main(args)

# genome = pickle.load(open('/Users/joelsimon/Projects/evoDesign/cppn/winner_genome.p'))

# print(evaluate(genome, verbose=True))
