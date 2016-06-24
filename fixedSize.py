import argparse
from src.experiment import Experiment

class FixedSize(Experiment):
    """docstring for FixedSize"""
    def __init__(self, *args, **kwargs):
        self.target = 100
        super(FixedSize, self).__init__(*args, **kwargs)

    def fitness(self, sim):
        n = len(sim.cells)
        fitness = 1 - abs(n-self.target)/float(self.target)
        return fitness

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--out', help='Output directory', default='./out/derp')
  parser.add_argument('-g', '--generations', help='', default=100, type=int)
  parser.add_argument('-c', '--cores', help='', default=1, type=int)
  args = parser.parse_args()

  experiment = FixedSize(out_dir=args.out, generations=args.generations,
                          cores=args.cores)
  experiment.run()
