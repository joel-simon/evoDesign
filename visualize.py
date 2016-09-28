from os.path import join
import sys
import os
import argparse
import pickle
import subprocess
# TODO allow passing experiment name
from examples.table import Simulation
from src.views.viewer import Viewer

def main(args):
    path = args.dir
    save = args.save
    tmp = None
    best_genome = pickle.load(open(join(path, 'genome.p'), 'rb'))
    
    viewer = Viewer(bounds=(8,8,8))

    if save:
        tmp = join(path, 'temp')
        os.system("rm -rf %s" % tmp)
        os.mkdir(tmp)
        video_path = join(path, 'animation.avi')

    simulation = Simulation(best_genome)
    simulation.verbose = True
    simulation.run(viewer=None)
    print 'animation done'
    # viewer.set_map(simulation.hmap)
    simulation.render_all(viewer)
    viewer.main_loop()

# if args.video:
    # if args.gif:
    # if save:
    #     subprocess.call(['avconv', '-i', join(tmp, '%d.jpg'),'-r','20',
    #                         '-threads', 'auto','-qscale','1','-s','800x800',
    #                         video_path])
    #     os.system("rm -rf %s" % tmp)
    #     print('Created video file.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    parser.add_argument('--save')
    args = parser.parse_args()
    main(args)
