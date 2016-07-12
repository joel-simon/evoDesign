import argparse
from src.experiment import Experiment
from src.physics.softPhysics2 import SoftPhysics
import math

class Height(Experiment):
  """docstring for Height"""
  def __init__(self, *args, **kwargs):
    super(Height, self).__init__(*args, **kwargs)

    # the target height.
    self.target = 20.

    # Simulation
    self.simulation_config['max_steps'] = 50
    self.simulation_config = {
      'max_steps': 100,
      'bounds' : 1000
    }

    # Physics
    self.physics = SoftPhysics
    self.physics_config = {}

    self.genome_config['inputs'] = [
      ('stress', lambda cell: cell.body.stress()),
      ('size', lambda cell: cell.body.size()/20),
      ('primary_angle_cos', lambda cell: math.cos(cell.body.angle)),
      ('primary_angle_sin', lambda cell: math.sin(cell.body.angle)),
    ]

    self.genome_config['outputs'] = [
      ('apoptosis', 'sigmoid', True),
      # ('divide_sin', 'tanh', False),
      # ('divide_cos', 'tanh', False),
      ('grow', 'sigmoid', False),
      ('contract_0', 'sigmoid', False)
      ('contract_1', 'sigmoid', False)
      ('divide', 'sigmoid', 0),
      # ('divide_1', 'sigmoid', 0),
    ]

  def set_up(self, sim):
      r = 6
      cell = sim.create_cell(position=(0, r), size=[r])

  def fitness(self, sim):
    if len(sim.cells) == 0:
      return 0
    h = max(c.body.position[1] for c in sim.cells)
    # print n
    # fitness = 1 - abs(n-self.target)/float(self.target)
    fitness = h/self.target
    # print fitness
    return fitness

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--out', help='Output directory', default='./out/derp')
  parser.add_argument('-g', '--generations', help='', default=100, type=int)
  parser.add_argument('-c', '--cores', help='', default=1, type=int)
  args = parser.parse_args()

  experiment = Height(out_dir=args.out, generations=args.generations,
                          cores=args.cores)
  experiment.run()
