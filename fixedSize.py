import argparse
from src.experiment import Experiment

class FixedSize(Experiment):
    """docstring for FixedSize"""
    def __init__(self, *args, **kwargs):
        super(FixedSize, self).__init__(*args, **kwargs)

        self.target = 100


        self.genome_config['inputs'] = [
          'stress',
          'size'
          # 'coverage'
        ]

        self.simulation_config = {
            'max_steps': 100,
            'bounds' : 1000
        }

        self.genome_config['outputs'] = [
          ('apoptosis', 'sigmoid', True),
          # ('divide_sin', 'tanh', False),
          # ('divide_cos', 'tanh', False),
          ('grow', 'sigmoid', False),

          ('divide0', 'sigmoid', 0),
          ('divide1', 'sigmoid', 0),
          ('divide2', 'sigmoid', 0),
          ('divide3', 'sigmoid', 0),
          # ('grow0', 'identity'),
          # ('grow1', 'identity')
        ]

    def set_up(self, sim):
      r = 30
      cell = sim.create_cell(position=(0, r), size=[r])

    def fitness(self, sim):
        n = len(sim.cells)
        fitness = 1 - abs(n-self.target)/float(self.target)
        return fitness

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--out', help='Output directory', default='./out/derp')
  parser.add_argument('-g', '--generations', help='', default=100, type=int)
  parser.add_argument('-p', '--population', help='', default=100, type=int)
  parser.add_argument('-c', '--cores', help='', default=1, type=int)
  args = parser.parse_args()

  experiment = FixedSize(out_dir=args.out, generations=args.generations,
                          cores=args.cores, population=args.population)
  experiment.run()
