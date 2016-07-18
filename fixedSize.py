import argparse

from src.experiment import Experiment, Input, Output, OutputCluster
from src.hexSimulation import Simulation

from src.hexVisualize import HexRenderer as Renderer

class FixedSize(Experiment):
    """docstring for FixedSize"""
    def __init__(self, *args, **kwargs):
        super(FixedSize, self).__init__(*args, **kwargs)

        self.target = 16
        self.Simulation = Simulation
        self.simulation_config = {
            'max_steps':40 ,
            'bounds':(8, 8),
            # 'verbose': True
            # 'Renderer': Renderer
        }

        # self.final_renderer = Renderer

        self.genome_config['inputs'] = [
            Input('neighbor_t',  lambda c,s:self.has_neighbor(c, s, 0)),
            Input('neighbor_tr', lambda c,s:self.has_neighbor(c, s, 1)),
            Input('neighbor_br', lambda c,s:self.has_neighbor(c, s, 2)),
            Input('neighbor_b',  lambda c,s:self.has_neighbor(c, s, 3)),
            Input('neighbor_bl', lambda c,s:self.has_neighbor(c, s, 4)),
            Input('neighbor_tl', lambda c,s:self.has_neighbor(c, s, 5)),
        ]
        # ('divide_sin', 'tanh', False),
        # ('divide_cos', 'tanh', False),
        # Out('grow', out='sigmoid', binary=False),

        self.genome_config['outputs'] = [
            Output('apoptosis', func=lambda c, s: s.destroy_cell(c) ),
            Output('divide_t',  func=lambda c, s: s.divide_cell(c, 0)),
            Output('divide_tr', func=lambda c, s: s.divide_cell(c, 1)),
            Output('divide_br', func=lambda c, s: s.divide_cell(c, 2)),
            Output('divide_b',  func=lambda c, s: s.divide_cell(c, 3)),
            Output('divide_bl', func=lambda c, s: s.divide_cell(c, 4)),
            Output('divide_tl', func=lambda c, s: s.divide_cell(c, 5))
            # OutputCluster(
            #     name='divide',
            #     outputs=[
            #         Output('0', type='sigmoid', binary=False),
            #         Output('1', type='sigmoid', binary=False),
            #         Output('2', type='sigmoid', binary=False),
            #         Output('3', type='sigmoid', binary=False),
            #         Output('4', type='sigmoid', binary=False),
            #         Output('5', type='sigmoid', binary=False)
            #     ],
            #     func=lambda cell, outs: cell.divide(outs.index(max(out)))
            # )
        ]

    def has_neighbor(self, cell, simulation, i):
        coords = simulation.hmap.neighbor(cell.userData['coords'], i)
        return int(simulation.hmap.is_occupied(coords))

    def set_up(self, sim):
        cell = sim.create_cell(coords=(0, 0))

    def fitness(self, sim):
        n = len(sim.cells)
        fitness = 1 - abs(n-self.target)/float(self.target)
        return fitness

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', help='Output directory', default='./out/derp')
    parser.add_argument('-g', '--generations', help='', default=4 , type=int)
    parser.add_argument('-p', '--population', help='', default=10, type=int)
    parser.add_argument('-c', '--cores', help='', default=1, type=int)
    args = parser.parse_args()

    experiment = FixedSize(out_dir=args.out, generations=args.generations,
                          cores=args.cores, population=args.population)
    experiment.run()
