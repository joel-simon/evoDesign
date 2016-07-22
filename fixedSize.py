# import pyximport; pyximport.install()
import argparse

# from src.experiment import Experiment#, Input, Output, OutputCluster
from src.hexSimulation import HexSimulation
# from src.hexRenderer import HexRenderer as Renderer

class FixedSize(HexSimulation):
    """docstring for FixedSize"""
    genome_config = {
        'num_morphogens': 1,
        'morphogen_thresholds': 4
    }
    genome_config['inputs'] = [
        'neighbor_t', 'neighbor_tr', 'neighbor_br', 'neighbor_b',
        'neighbor_bl', 'neighbor_tl', 'a0','a1','a2','a3'
    ]
    genome_config['outputs'] = [
        'apoptosis', 'divide_t', 'divide_tr', 'divide_br',
        'divide_b', 'divide_bl', 'divide_tl', 'a0', 'i0'
    ]
    def __init__(self, genome):
        super(FixedSize, self).__init__(genome,
            max_steps = 40, bounds=(16,16))
        self.target = 60
        # self.genome_config['inputs'] = [
        #     'neighbor_t', 'neighbor_tr', 'neighbor_br', 'neighbor_b',
        #     'neighbor_bl', 'neighbor_tl'
        #     Input('neighbor_t',  lambda c,s:self.has_neighbor(c, s, 0)),
        # ]
        # ('divide_sin', 'tanh', False),
        # ('divide_cos', 'tanh', False),
        # Out('grow', out='sigmoid', binary=False),

        # self.genome_config['outputs'] = [
        #     'apoptosis', 'divide_t', 'divide_tr', 'divide_br'
        #     'divide_b', 'divide_bl', 'divide_tl'

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

    def _morphogen_inputs(self, cell):
        """Get the morphogens threshholds
        """
        inputs = [0.0] * 4
        coords = cell.userData['coords']
        value = self.A[coords[0]][coords[1]]
        max_value = 10
        p = value/max_value
        p = min(p, .9999)
        inputs[int(p*4)] = 1
        return inputs

    def create_inputs(self, cell):
        # inputs = []
        coords = cell.userData['coords']
        inputs = list(map(bool, self.hmap.neighbors(coords)))
        inputs.extend(self._morphogen_inputs(cell))
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


        # Update the morphogen production amounts
        coords = cell.userData['coords']
        self.PA[coords[0]][coords[1]] = outputs[-2]
        self.PI[coords[0]][coords[1]] = outputs[-1]


    def set_up(self):
        cell = self.create_cell(coords=(8, 8))

    def fitness(self, sim):
        # n = len(sim.cells)
        # fitness = 1 - abs(n-self.target)/float(self.target)
        # fitness = min(.95, fitness)
        # return fitness
        # score = 0
        TP = 0.0
        FN = 0.0
        FP = 0.0
        dist = 4

        cent = (8,8)
        for row in range(16):
            for col in range(16):
                if self.hmap.distance(cent, (row,col) ) <= dist:
                    if self.hmap[row][col]:
                        TP += 1
                    else:
                        FN += 1
                else:
                    if self.hmap[row][col]:
                        FP += 1
                    else:
                        pass
        return TP / (TP + FN + FP)
