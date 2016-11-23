from os.path import join
import os
import argparse
import pickle
from src.views.viewer import Viewer
from src import export

from examples.plant.plant import Plant as Simulation
def main(args):
    path = args.dir
    save = args.save
    best_genome = pickle.load(open(join(path, 'genome.p'), 'rb'))
    # Simulation = pickle.load(open(join(path, 'simulation.p')))
    sim_params = pickle.load(open(join(path, 'params.p')))

    # tmp = None
    # if save:
    #     tmp = join(path, 'temp')
    #     os.system("rm -rf %s" % tmp)
    #     os.mkdir(tmp)
    #     video_path = join(path, 'animation.avi')

    for i, params in enumerate(sim_params):
        viewer = Viewer(bounds=(8, 8, 8))
        simulation = Simulation(best_genome, **params)
        simulation.run()

        max_steps = simulation.max_fitness_steps
        simulation = Simulation(best_genome, **params)
        simulation.verbose = True
        simulation.max_steps = max_steps + 1
        simulation.run(viewer=viewer)

        export.to_obj(simulation.hmap, join(path, 'final_obj_%i.obj'%i))
        simulation.render_all(viewer)
        print('Animation done.')
        viewer.main_loop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input directory')
    parser.add_argument('--save')
    args = parser.parse_args()
    main(args)
