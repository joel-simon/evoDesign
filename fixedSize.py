import pyximport; pyximport.install()
import argparse

# from src.experiment import Experiment#, Input, Output, OutputCluster
from src.hexSimulation import HexSimulation
from src.hexRenderer import HexRenderer as Renderer

class FixedSize(HexSimulation):
    """docstring for FixedSize"""
    genome_config = {
        'num_morphogens': 0,
        'morphogen_thresholds': 0
    }
    genome_config['inputs'] = [
        'neighbor_t', 'neighbor_tr', 'neighbor_br', 'neighbor_b',
        'neighbor_bl', 'neighbor_tl'
    ]
    genome_config['outputs'] = [
        'apoptosis', 'divide_t', 'divide_tr', 'divide_br',
        'divide_b', 'divide_bl', 'divide_tl'
    ]
    def __init__(self, genome):
        super(FixedSize, self).__init__(genome, max_steps = 40, bounds=(16,16))
        self.target = 255
        # self.genome_config['inputs'] = [
        #     'neighbor_t', 'neighbor_tr', 'neighbor_br', 'neighbor_b',
        #     'neighbor_bl', 'neighbor_tl'
        #     Input('neighbor_t',  lambda c,s:self.has_neighbor(c, s, 0)),
        #     Input('neighbor_tr', lambda c,s:self.has_neighbor(c, s, 1)),
        #     Input('neighbor_br', lambda c,s:self.has_neighbor(c, s, 2)),
        #     Input('neighbor_b',  lambda c,s:self.has_neighbor(c, s, 3)),
        #     Input('neighbor_bl', lambda c,s:self.has_neighbor(c, s, 4)),
        #     Input('neighbor_tl', lambda c,s:self.has_neighbor(c, s, 5)),
        # ]
        # ('divide_sin', 'tanh', False),
        # ('divide_cos', 'tanh', False),
        # Out('grow', out='sigmoid', binary=False),

        # self.genome_config['outputs'] = [
        #     'apoptosis', 'divide_t', 'divide_tr', 'divide_br'
        #     'divide_b', 'divide_bl', 'divide_tl'
        #     Output('apoptosis', func=lambda c, s: s.destroy_cell(c) ),
        #     Output('divide_t',  func=lambda c, s: s.divide_cell(c, 0)),
        #     Output('divide_tr', func=lambda c, s: s.divide_cell(c, 1)),
        #     Output('divide_br', func=lambda c, s: s.divide_cell(c, 2)),
        #     Output('divide_b',  func=lambda c, s: s.divide_cell(c, 3)),
        #     Output('divide_bl', func=lambda c, s: s.divide_cell(c, 4)),
        #     Output('divide_tl', func=lambda c, s: s.divide_cell(c, 5))
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
        # ]

    def create_inputs(self, cell):
        # inputs = []
        coords = cell.userData['coords']
        inputs = list(map(bool, self.hmap.neighbors(coords)))
        return inputs

    def handle_outputs(self, cell, outputs):
        if outputs[0] > .5:
            self.destroy_cell(cell)
            return
        if outputs[1] > .5:
            self.divide_cell(cell, 0)
        if outputs[2] > .5:
            self.divide_cell(cell, 1)
        if outputs[3] > .5:
            self.divide_cell(cell, 2)
        if outputs[4] > .5:
            self.divide_cell(cell, 3)
        if outputs[5] > .5:
            self.divide_cell(cell, 4)
        if outputs[6] > .5:
            self.divide_cell(cell, 5)

    def set_up(self):
        cell = self.create_cell(coords=(0, 0))

    def fitness(self, sim):
        n = len(sim.cells)
        fitness = 1 - abs(n-self.target)/float(self.target)
        fitness = min(.95, fitness)
        return fitness
