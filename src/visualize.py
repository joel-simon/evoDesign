
def main(args):
  import pickle
  import sys
  import random
  from simulation import Simulation
  path = args.dir

  # with open(join(path, 'population.p'), 'rb') as f:
  #   pop = pickle.load(f)#, encoding='latin1')

  with open(join(path, 'genome.p'), 'rb') as f:
    best_genome = pickle.load(f)#, encoding='latin1')

  video_path = join(path, 'animation.avi')
  save = args.save

  physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=600.0,
                                        damping=0.5, timestep = .03, save=save)

  # best_genome = pop.statistics.best_genome()
  sim = Simulation(best_genome, physics, (800, 800), render=plot, verbose=True)

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

# if __name__ == '__main__':
#   parser = argparse.ArgumentParser()
#   parser.add_argument('dir', help='Input directory')
#   parser.add_argument('--save')
#   args = parser.parse_args()
#   main(args)
