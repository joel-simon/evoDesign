from os.path import join
import sys
import os
import argparse
import pickle

# from src.simulation import Simulation
# from src.box2DPhysics import Box2DPhysicsRender

# def main(args):
#   path = args.dir
#   with open(join(path, 'population.p'), 'rb') as f:
#     pop = pickle.load(f)

#   best_genome = pop.statistics.best_genome()
#   physics = Box2DPhysicsRender(verbose=True, max_steps=999)

#   sim = Simulation(best_genome, physics, max_steps=100, verbose=True)
#   sim.create_cell(position=(0, 1), size=[1, 1])
#   sim.run()

# if __name__ == '__main__':
#   parser = argparse.ArgumentParser()
#   parser.add_argument('dir', help='Input directory')
#   parser.add_argument('--save')
#   args = parser.parse_args()
#   main(args)


def main(args):
  import pickle
  import sys
  import random
  from src.hexSimulation import Simulation
  path = args.dir

  with open(join(path, 'population.p'), 'rb') as f:
    pop = pickle.load(f, encoding='latin1')

  # with open(join(path, 'genome.p'), 'rb') as f:
  #   best_genome = pickle.load(f)#, encoding='latin1')

  video_path = join(path, 'animation.avi')
  save = args.save

  best_genome = pop.statistics.best_genome()
  sim = Simulation(best_genome, bounds=(15, 15), verbose=True)
  sim.renderer = HexRenderer(sim)

  sim.run(80)
  print('run over')

  if save:
    subprocess.call(['avconv','-i','temp/%d.jpg','-r','12',
                    '-threads','auto','-qscale','1','-s','800x800', video_path])
    os.system("rm -rf temp")
    print('Created video file.')

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

# def main():
#   import pickle
#   import sys
#   import random
#   from simulation import Simulation
#   path = args.dir

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('dir', help='Input directory')
  parser.add_argument('--save')
  args = parser.parse_args()
  main(args)
