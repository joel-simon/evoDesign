import numpy as np
from datetime import datetime
import argparse
import pickle
from os.path import join

from examples.bookcase.bookcase import BookCase
from itertools import product, repeat
from random import sample

from multiprocessing import Pool


def get_items(a, mean_height, height_std, height_min=2, height_max=5):
    items = []
    depth = 2
    n_items = int(a/float(mean_height) * 1.25)
    heights = np.random.normal(mean_height, height_std, [n_items]).astype(int)
    heights[heights < height_min] = height_min
    heights[heights > height_max] = height_max
    items = [(h, depth) for h in heights]
    return items

def evaluate(args):
    genome, bounds = args
    items = get_items(bounds[0]*bounds[1], 3, 1)
    sim = BookCase(genome, bounds=bounds, items=items)
    sim.run()
    return sim.max_fitness

def main(args):
    path = args.dir
    pool = Pool(6)
    genome = pickle.load(open(join(path, 'genome.p'), 'rb'))
    sim_params = pickle.load(open(join(path, 'params.p')))

    train = (param['bounds'] for param in sim_params)
    test = ((x,y,4) for x,y in product(range(4,20,4),range(4,20,4)) if x*y > 20)
    print list(test)
    # bounds = sample(set(test).difference(set(train)), 100)
    # scores = dict(zip(bounds, pool.map(evaluate, zip(repeat(genome), bounds))))

    # pickle.dump(scores, open('./test_results.p', 'wb'))
    # print('Done')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    # parser.add_argument('--save')
    args = parser.parse_args()
    main(args)

