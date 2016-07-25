from os.path import join
import sys
import os
import argparse
import pickle
import subprocess
# TODO allow passing experiment name
from fixedSize import FixedSize as Simulation
from src.hexRenderer import HexRenderer as Renderer


def main(args):
    path = args.dir
    save = args.save

    with open(join(path, 'winner.p'), 'rb') as f:
        best_genome = pickle.load(f)

    # Visualize the best network.
    node_names = dict()
    for i, name in enumerate(best_genome.inputs + best_genome.outputs):
        node_names[i] = name

    tmp = None
    if save:
        tmp = join(path, 'temp')
        os.system("rm -rf %s" % tmp)
        os.mkdir(tmp)

        video_path = join(path, 'animation.avi')


    if Renderer:
        renderer = Renderer(save=tmp)
        simulation = Simulation(best_genome)
        simulation.verbose = True
        simulation.run(renderer)


    if save:
        # subprocess.call(['avconv', '-i', join(tmp, '%d.jpg'),'-r','20',
        #                     '-threads', 'auto','-qscale','1','-s','800x800',
        #                     video_path])
        # os.system("rm -rf %s" % tmp)
        print('Created video file.')

    # if Renderer:
    #     renderer.hold()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    parser.add_argument('--save')
    args = parser.parse_args()
    main(args)
