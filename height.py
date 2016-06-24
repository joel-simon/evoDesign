import argparse
from src.experiment import Experiment
from src.box2DPhysics import Box2DPhysics, Box2DPhysicsRender

class Height(Experiment):
  """docstring for Height"""
  def __init__(self, *args, **kwargs):
    super(Height, self).__init__(*args, **kwargs)
    self.target = 4.
    self.simulation_config['max_steps'] = 50

    self.physics = Box2DPhysics
    self.physicsVisual = Box2DPhysicsRender
    self.physics_config = {}

  def set_up(self, sim):
    sim.create_cell(position=(0, 1), size=[1, 1])

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
